# 1. 베이스 이미지 설정 (Python 3.11 Slim 버전 사용으로 용량 최적화)
FROM python:3.11-slim

# 2. 필수 패키지 설치 (lxml 등 컴파일이 필요한 라이브러리 대응)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 의존성 파일 복사 및 설치
# gemini_req.txt 파일을 컨테이너 내 gemini_req.txt로 복사
COPY gemini_req.txt .
RUN pip install --no-cache-dir -r gemini_req.txt

# 5. 소스 코드 복사
COPY . .

# 6. Gradio 기본 포트 노출
EXPOSE 7860

# 7. 앱 실행 (0.0.0.0으로 실행하여 외부 접속 허용)
CMD ["python", "app.py"]