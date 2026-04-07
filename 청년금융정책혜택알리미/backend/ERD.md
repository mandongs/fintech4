# ERD 및 API 명세

## 테이블 설계

### users — 사용자
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| email | VARCHAR(255) UNIQUE | |
| hashed_password | VARCHAR | |
| created_at | TIMESTAMP | |

### user_profiles — 사용자 프로필 (매칭 조건)
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| birth_date | DATE | 생년월일 → 나이 계산 |
| annual_income | INTEGER | 연소득 (만원) |
| region_code | VARCHAR(10) | 시군구코드 (e.g. 11110) |
| region_name | VARCHAR(50) | 지역명 (e.g. 서울 종로구) |
| marriage_status | VARCHAR(10) | 미혼/기혼/이혼 |
| job_code | VARCHAR(10) | 직업코드 |
| school_code | VARCHAR(10) | 학력코드 |
| employment_type | VARCHAR(20) | 재직/구직/자영업/프리랜서 |
| persona | VARCHAR(30) | 공격적저축형/안정형 등 (자동 계산) |
| updated_at | TIMESTAMP | |

### policies — 청년 정책
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | VARCHAR PK | plcyNo |
| name | VARCHAR(200) | 정책명 |
| category_main | VARCHAR(50) | 대분류 (일자리/주거/교육 등) |
| category_sub | VARCHAR(50) | 소분류 |
| description | TEXT | 설명 |
| support_content | TEXT | 지원내용 |
| apply_method | TEXT | 신청방법 |
| apply_url | VARCHAR(500) | 신청URL |
| min_age | INTEGER | 최소 나이 (0=제한없음) |
| max_age | INTEGER | 최대 나이 (0=제한없음) |
| earn_min | INTEGER | 최소 소득 (만원, 0=제한없음) |
| earn_max | INTEGER | 최대 소득 (만원, 0=제한없음) |
| region_codes | TEXT | 지역코드 콤마구분 (NULL=전국) |
| marriage_code | VARCHAR(10) | 결혼상태코드 |
| job_codes | TEXT | 직업코드 콤마구분 |
| school_codes | TEXT | 학력코드 콤마구분 |
| apply_start | DATE | 신청 시작일 |
| apply_end | DATE | 신청 마감일 |
| apply_period_text | VARCHAR(100) | 원본 기간 텍스트 |
| biz_start | DATE | 사업기간 시작 |
| biz_end | DATE | 사업기간 종료 |
| supervise_inst | VARCHAR(100) | 주관기관 |
| operate_inst | VARCHAR(100) | 운영기관 |
| view_count | INTEGER DEFAULT 0 | |
| embedding_id | INTEGER | FAISS index id |
| fetched_at | TIMESTAMP | 수집일시 |
| updated_at | TIMESTAMP | |

### financial_products — 금융상품
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | VARCHAR PK | 금융회사코드+상품코드 |
| company_code | VARCHAR(20) | 금융회사코드 |
| company_name | VARCHAR(100) | 회사명 |
| product_code | VARCHAR(50) | 상품코드 |
| product_name | VARCHAR(200) | 상품명 |
| product_type | VARCHAR(20) | saving/deposit/mortgage/rent/credit |
| join_method | VARCHAR(100) | 가입방법 |
| target_raw | TEXT | 가입대상 (원본) |
| is_youth_product | BOOLEAN | 청년 특화 여부 |
| min_age | INTEGER | 파싱된 최소 나이 |
| max_age | INTEGER | 파싱된 최대 나이 |
| preferred_condition | TEXT | 우대조건 |
| max_limit | BIGINT | 최대한도 |
| start_date | DATE | 공시 시작일 |
| end_date | DATE | 공시 종료일 |
| dcls_month | VARCHAR(10) | 공시월 (e.g. 202603) |
| fetched_at | TIMESTAMP | |

### user_bookmarks — 관심 정책 북마크
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| policy_id | VARCHAR FK → policies | |
| notify_enabled | BOOLEAN DEFAULT true | D-day 알림 여부 |
| created_at | TIMESTAMP | |

### notification_logs — 알림 발송 이력
| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| policy_id | VARCHAR FK → policies | |
| days_left | INTEGER | 발송 시점 D-day |
| sent_at | TIMESTAMP | |

---

## API 명세

### Auth
| Method | Path | 설명 |
|--------|------|------|
| POST | /api/auth/register | 회원가입 |
| POST | /api/auth/login | 로그인 (JWT 반환) |
| POST | /api/auth/refresh | 토큰 갱신 |

### Profile
| Method | Path | 설명 |
|--------|------|------|
| GET | /api/profile | 내 프로필 조회 |
| POST | /api/profile | 프로필 생성/수정 |

### Recommend
| Method | Path | 설명 |
|--------|------|------|
| GET | /api/recommend/policies | 매칭 정책 목록 (점수순) |
| GET | /api/recommend/financial | 매칭 금융상품 목록 |

### Alert
| Method | Path | 설명 |
|--------|------|------|
| GET | /api/alerts | D-day 임박 정책 목록 |
| POST | /api/bookmarks/{policy_id} | 북마크 등록 |
| DELETE | /api/bookmarks/{policy_id} | 북마크 해제 |
| GET | /api/bookmarks | 내 북마크 목록 |

### Policy
| Method | Path | 설명 |
|--------|------|------|
| GET | /api/policies | 정책 목록 (필터/검색) |
| GET | /api/policies/{id} | 정책 상세 |

### Chat
| Method | Path | 설명 |
|--------|------|------|
| POST | /api/chat | AI 질의응답 (스트리밍) |

### Batch (내부)
| Method | Path | 설명 |
|--------|------|------|
| POST | /api/batch/collect-fss | FSS 금융상품 수집 트리거 |
| POST | /api/batch/collect-policy | 청년정책 수집 트리거 |
| POST | /api/batch/send-alerts | D-day 알림 발송 트리거 |
