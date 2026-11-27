# langchain-report-assistant 작업 보고서

작성일 2026-11-27 · 프로젝트 경로 `C:\workspace\20261127\langchain-report-assistant`

---

## 1. 한눈에 보기

| 지표 | 값 |
|---|---|
| 구현한 app 모듈 | 11 / 24개 (46%) |
| 작성한 파이썬 파일 | 17개 (app 11 · scripts 5 · tests 1) |
| 작성한 코드 줄 수 | 578줄 (app 399 · scripts 140 · tests 39) |
| 열려 있는 API 경로 | 5개 |
| 해결한 오류 | 7건 |
| 남은 이슈 | 1건 (`.env` 1번째 줄 parse 경고) |

---

## 2. 동작 확인 결과

| 항목 | 결과 | 비고 |
|---|---|---|
| `GET /health` | 200 OK | 서버 생존 확인 |
| `GET /health/ready` | ready | DB 연결 · pgvector 설치 · 테이블 11개 모두 정상 |
| `POST /api/v1/agent/ask` | 200 OK | 현재는 stub 응답 (LLM 미연결) |
| GPU(CUDA) 임베딩 | 정상 | E5 모델 로딩과 질문 임베딩까지 통과 |
| pgvector Top-k 검색 | 코드 완성 | 검색 결과 확인 전 (4단계 참고) |

---

## 3. API 경로 (5개)

| 번호 | 방식 | 경로 | 역할 | 상태 |
|---|---|---|---|---|
| 1 | GET | `/` | 서비스 정보 | 완료 |
| 2 | GET | `/health` | 서버 생존 확인 | 완료 |
| 3 | GET | `/health/ready` | DB · pgvector 준비 확인 | 완료 |
| 4 | POST | `/api/v1/agent/ask` | 질문 접수 | stub |
| 5 | GET | `/docs` | Swagger 화면 | 완료 |

---

## 4. 폴더 트리 진행률

### app 모듈 11 / 24

| 영역 | 완료 | 남음 |
|---|---|---|
| 진입 · 에이전트 | `main.py`, `agent.py`(stub) | - |
| api | `api/agent.py` | `api/rag.py` |
| core | `settings.py`, `preflight.py` | `runtime.py` |
| db | `connection.py`, `repository.py` | - |
| rag | `embeddings.py`, `retriever.py`, `documents.py` | `ids.py`, `reranker.py`, `pipeline.py`, `query_optimizer.py` |
| tools | - | `rag_tool.py`, `db_tool.py` |
| schemas | `agent.py` | `tools.py` |
| services | - | `validator.py`, `errors.py`, `metrics.py`, `run_store.py` |
| **합계** | **11** | **13** |

### 그 밖의 폴더

| 항목 | 계획 | 완료 |
|---|---|---|
| `scripts/` (계획) | 2개 | 2개 (`preflight.py`, `verify_live.py`) |
| `scripts/` (추가 도구) | - | 3개 (`inspect_db.py`, `try_retrieve.py`, `check_env.py`) |
| `tests/` | pytest 계약 테스트 | 1개 파일 (`test_health.py`, 테스트 5개) |
| `test/` | `000~016_test.py` 17개 | 0개 |
| `evaluation/`, `data/evaluation/` | Intermediate 이상 | 0개 |

---

## 5. 데이터베이스 구조 (확인된 값)

| 테이블 | 행 수 | 용도 |
|---|---|---|
| `reports` | 184 | 보고서 공통 정보 (`overview` 요약, 분류, 인덱스 상태, 버전) |
| `report_embeddings` | 184 | 벡터 `vector(384)` 저장 |
| `daily_work_reports` | 30 | 일일 업무 보고서 |
| `data_processing_reports` | 30 | 데이터 처리 보고서 |
| `experiment_reports` | 34 | 실험 보고서 |
| `meeting_minutes` | 30 | 회의록 |
| `prompt_reports` | 30 | 프롬프트 보고서 |
| `research_plans` | 30 | 연구 계획서 |
| `prompt_versions` | 60 | 프롬프트 버전 |
| `report_categories` | 6 | 보고서 분류 |

확인된 점

| 점검 항목 | 값 |
|---|---|
| 종류별 보고서 합계 | 30 + 30 + 34 + 30 + 30 + 30 = 184 (`reports`와 일치) |
| 벡터 차원 | 384 |
| DB 전체 테이블 수 | 11 (위 표는 그중 출력된 10개) |

---

## 6. 검색 구조

| 구분 | 내용 |
|---|---|
| 검색 대상 | `report_embeddings.embedding` (코사인 거리) |
| 돌려주는 텍스트 | `reports.overview` (1,000자 이하) |
| 함께 돌려주는 정보 | 분류 이름, 인덱스 상태, 오래된 벡터 여부 |
| 기본 Top-k | 5 |
| 임베딩 모델 기본값 | `intfloat/multilingual-e5-small` (384차원) |
| 질문 접두어 | `query: ` 자동 부착 |
| 안전장치 | DB에 저장된 모델 이름과 다르면 오류로 알려줌 |
| 보고서 본문 | 종류별 테이블에 있음 (`db_tool`에서 조회 예정) |

---

## 7. 해결한 오류 (7건)

| 번호 | 증상 | 원인 | 조치 |
|---|---|---|---|
| 1 | `WinError 10061` | 서버가 떠 있지 않은 상태에서 확인 스크립트 실행 | 서버 실행 후 새 터미널에서 재실행 |
| 2 | `/ask` 404 | 주소와 방식이 틀림 (`/api/v1/agent/ask`, POST) | 정확한 경로와 Swagger 사용 |
| 3 | Swagger에 경로 없음 | `main.py`에 라우터 연결 누락 | 라우터 연결 버전으로 교체 |
| 4 | `cannot import name 'run_agent'` | `app/agent.py`가 빈 파일 | 함수 작성 |
| 5 | 순환 임포트 | `schemas/agent.py`가 자기 자신을 임포트 | 파일 내용 교정 |
| 6 | `/health/ready` 503 (`missing "="`) | `.env`의 `postgresql+psycopg://` 형식 | 주소 변환 코드 추가 |
| 7 | `"chunks" 릴레이션 없음` | 테이블 이름을 추측으로 작성 | 실제 구조(`reports` + `report_embeddings`)에 맞춰 재작성 |

남은 이슈

| 번호 | 증상 | 확인 방법 |
|---|---|---|
| 1 | `python-dotenv could not parse statement starting at line 1` | `python scripts/check_env.py` |

---

## 8. 결론: 다음 진행 순서

| 순서 | 작업 | 대상 파일 | 완료 기준 |
|---|---|---|---|
| 1 | 검색 결과 확인과 모델 이름 일치 확인 | `scripts/try_retrieve.py` | 질문과 관련된 보고서가 Top-3에 나옴 |
| 2 | `.env` 경고 해결 | `scripts/check_env.py` | parse 경고가 사라짐 |
| 3 | 보고서 본문 조회 도구 | `tools/db_tool.py`, `tools/rag_tool.py`, `rag/ids.py` | `report_id`로 종류별 본문을 가져옴 |
| 4 | LLM 연결 (`create_agent` + Structured Output) | `app/agent.py`, `schemas/agent.py` | stub 대신 실제 답변이 나옴 |
| 5 | 출력검사 · 근거검토 · 오류 처리 | `services/validator.py`, `errors.py` | 잘못된 출력이 오류 응답으로 걸러짐 |
| 6 | 단계별 조립 | `core/runtime.py`, `rag/pipeline.py` | `/ask` 한 번에 검색부터 답변까지 처리 |
| 7 | 검증과 정리 | `test/000~016_test.py`, `tests/`, `README.md`, `outputs/` | 테스트 통과와 산출물 저장 |

선택 확장 (7단계 이후): `reranker.py`, `query_optimizer.py`, `evaluation/`, `run_store.py`
