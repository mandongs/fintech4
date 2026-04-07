"""
Gemini RAG 기반 AI 질의응답 서비스.
노트북의 answer_question / build_personalized_prompt 로직을 이식.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd
import tiktoken

from app.core.config import settings
from app.models.policy import Policy
from app.models.user import UserProfile
from app.services.matching import categorize_persona, compute_age

logger = logging.getLogger(__name__)

MAX_CONTEXT_TOKENS = 12_000
EMBED_ENCODING = "cl100k_base"

_tokenizer = tiktoken.get_encoding(EMBED_ENCODING)
_faiss_index = None
_embed_df: pd.DataFrame | None = None
_genai_client = None


def _get_client():
    global _genai_client
    if _genai_client is None:
        from google import genai
        _genai_client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    return _genai_client


def _load_faiss():
    global _faiss_index, _embed_df
    if _faiss_index is not None:
        return

    faiss_path = Path(settings.FAISS_INDEX_PATH)
    embed_path = Path(settings.POLICY_EMBED_PATH)

    if not faiss_path.exists() or not embed_path.exists():
        logger.warning("[AIChat] FAISS 인덱스가 없습니다. 벡터 검색을 건너뜁니다.")
        return

    import faiss
    _faiss_index = faiss.read_index(str(faiss_path))
    _embed_df = pd.read_csv(embed_path)
    logger.info(f"[AIChat] FAISS 인덱스 로드 완료: {_faiss_index.ntotal}개 벡터")


async def _embed_query(text: str) -> np.ndarray:
    client = _get_client()
    from google.genai import types
    result = client.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return np.array(result.embeddings[0].values, dtype=np.float32)


def _vector_search(query_vec: np.ndarray, top_k: int = 5) -> list[str]:
    """FAISS 검색 → policy id 목록 반환."""
    _load_faiss()
    if _faiss_index is None or _embed_df is None:
        return []
    vec = query_vec.reshape(1, -1)
    _, indices = _faiss_index.search(vec, top_k)
    ids = []
    for idx in indices[0]:
        if idx < 0 or idx >= len(_embed_df):
            continue
        ids.append(str(_embed_df.iloc[idx].get("id", "")))
    return [i for i in ids if i]


def _count_tokens(text: str) -> int:
    return len(_tokenizer.encode(text))


def _truncate_context(texts: list[str], max_tokens: int = MAX_CONTEXT_TOKENS) -> str:
    result, total = [], 0
    for t in texts:
        n = _count_tokens(t)
        if total + n > max_tokens:
            break
        result.append(t)
        total += n
    return "\n\n---\n\n".join(result)


def _build_policy_context(policies: list[Policy]) -> str:
    parts = []
    for p in policies:
        chunk = f"[{p.name}]\n"
        if p.description:
            chunk += f"설명: {p.description}\n"
        if p.support_content:
            chunk += f"지원내용: {p.support_content}\n"
        if p.apply_url:
            chunk += f"신청: {p.apply_url}\n"
        if p.apply_period_text:
            chunk += f"신청기간: {p.apply_period_text}\n"
        if p.min_age or p.max_age:
            chunk += f"나이: {p.min_age}~{p.max_age}세\n"
        parts.append(chunk)
    return _truncate_context(parts)


def _build_system_prompt(profile: UserProfile | None, policy_context: str) -> str:
    profile_txt = ""
    if profile:
        age = compute_age(profile.birth_date) if profile.birth_date else "미입력"
        persona = categorize_persona(profile) if profile.birth_date else "미분류"
        profile_txt = f"""
사용자 프로필:
- 나이: {age}세
- 연소득: {profile.annual_income or '미입력'}만원
- 지역: {profile.region_name or '미입력'}
- 고용상태: {profile.employment_type or '미입력'}
- 결혼상태: {profile.marriage_status or '미입력'}
- 페르소나: {persona}
"""

    return f"""당신은 청년 금융 혜택 전문 상담 AI입니다.
사용자의 질문에 대해 아래 정책 정보를 근거로 정확하고 친절하게 답변하세요.
정책 정보에 없는 내용은 추측하지 말고 "확인이 필요합니다"라고 안내하세요.
답변은 한국어로, 마크다운 형식(불릿, 볼드)을 활용해 읽기 쉽게 작성하세요.

{profile_txt}

[참고 정책 정보]
{policy_context}
"""


async def answer_question(
    question: str,
    history: list[dict],
    profile: UserProfile | None,
    policies_from_db: list[Policy],
) -> str:
    """
    질문 → Gemini RAG 답변 생성.
    history: [{"role": "user"|"model", "parts": "..."}]
    """
    # 1) 벡터 검색으로 관련 정책 추가 검색
    try:
        query_vec = await _embed_query(question)
        vector_ids = _vector_search(query_vec, top_k=5)
        # DB 정책과 합쳐서 중복 제거
        db_ids = {p.id for p in policies_from_db}
        extra_ids = [i for i in vector_ids if i not in db_ids]
        all_policies = list(policies_from_db)
        # extra_ids에 해당하는 정책은 DB에서 별도 조회 필요하나 여기선 생략 (id만 있음)
    except Exception as e:
        logger.warning(f"[AIChat] 벡터 검색 실패 (무시): {e}")
        all_policies = list(policies_from_db)

    # 2) 컨텍스트 구성
    policy_context = _build_policy_context(all_policies[:10])
    system_prompt = _build_system_prompt(profile, policy_context)

    # 3) Gemini 호출
    client = _get_client()
    from google.genai import types

    contents = []
    for h in history[-6:]:   # 최근 6턴만 유지
        contents.append(types.Content(role=h["role"], parts=[types.Part(text=h["parts"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=question)]))

    response = client.models.generate_content(
        model=settings.GENERATION_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
            max_output_tokens=1024,
        ),
    )
    return response.text or "답변을 생성하지 못했습니다."
