# Topic Evolution TODO (Pending C/G)

## 상태
- Vision/plan 문서 작성됨: `docs/design/news_weather_map_vision.md`, `docs/design/topic_evolution_implementation.md`
- 코드/DB/파이프라인/프론트 작업은 미착수 (C 부재)

## 다음 단계 (합의/승인 필요)
1) 스키마 추가 (Supabase)
   - 새 테이블: `mvp_topic_history`, `mvp_topic_relationships`
   - 마이그레이션 파일 작성 후 적용 여부 결정
2) 스크립트
   - `data/pipelines/detect_topic_evolution.py` 구현 (어제→오늘 토픽 유사도, NEW/CONT/ SPLIT/MERGE/END 분류, 저장)
   - `aggregate_megatopics.py` 끝에서 진화 감지 호출 통합
3) API
   - `/api/topics/evolution`, `/api/topics/[id]/timeline` 등 관계/타임라인 반환
4) 프론트
   - `/topics/timeline` 페이지(리스트/그래프), 메인 피드에 진화 배지/요약 추가

## 의존/결정 사항
- 기준 테이블: `mvp_topics` vs `topics` 중 어떤 것을 진화 대상 메인으로 사용할지 합의
- 임계값/매칭 룰: 유사도 threshold, 분화/병합 판정 규칙 확정
- GA 파이프라인: RSS→DB 전환 여부 확정 후 스크립트 호출 순서 반영

## C/G 요청 메모 (복귀 후)
- C: 스키마 적용 확인 후 API/프론트 구현 시작
- G: 진화 탐지 스크립트 구현 및 파이프라인 통합, 임계값 튜닝
