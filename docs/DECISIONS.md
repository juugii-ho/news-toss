# Architecture & Policy Decisions

> 이 문서는 프로젝트의 주요 기술 및 정책에 대한 의사결정 기록을 관리합니다.
> `docs/TEMPLATES.md`의 형식을 준수하여 작성합니다.

## DT-002: MVP 기획 명세서 v1.0 세부 정책 구체화

## DT-003: Local 탭 트렌드 스코어 도입

**제안자**: G
**날짜**: 2025-11-28
**관련 TASK**: TASK-002 (추후 WORK.md에 추가 예정)

### 문제 (Problem)
- 현재 Local 탭의 모자이크 레이아웃 크기는 '기사 수(article_count)'에만 의존합니다. 이는 중요도가 떨어지거나 오래된 토픽도 기사 수가 많다는 이유로 계속 크게 노출될 수 있어, '지금 뜨는' 트렌드를 반영하는 데 한계가 있습니다. 사용자는 '규모감'과 함께 '역동적인 트렌드'를 느끼기를 기대합니다.

### 제안 (Proposal)
- '기사 수(article_count)'와 '시간(time)' 요소를 결합한 **'트렌드 스코어(Trend Score)'**를 도입하여, 토픽의 시의성을 반영하겠습니다.
  - **계산식 (예시)**: `trend_score = article_count / ((현재 시각 - 토픽 생성 시각) / 1시간 단위 + 1)`
  - **효과**: 새로운 토픽이 빠르게 부상할 때, 기사 수가 상대적으로 적더라도 높은 트렌드 스코어를 받아 더 크게 노출될 수 있습니다. (예: 생성 1시간 내 100개 기사 = 100점, 생성 24시간 내 100개 기사 = 약 4점)
  - `display_level` 할당 시 `article_count` 대신 `trend_score`를 주 기준으로 활용합니다.

### Reviews (다른 Agent 의견)
- N/A

### Final Decision by S
-
---


**제안자**: G
**날짜**: 2025-11-28
**관련 TASK**: N/A (초기 기획 구체화)

### 문제 (Problem)
- MVP 기획 명세서 v1.0의 일부 데이터 정책 및 커뮤니케이션 프로토콜에 대한 명확한 정의가 필요했습니다.

### 제안 (Proposal)
- G가 제기한 질문들에 대해 S가 정책을 확정하고, 이를 모든 에이전트가 따르도록 기록합니다.

### Reviews (다른 Agent 의견)
- N/A (S와 G 간의 직접적인 논의 및 결정)

### Final Decision by S
- **승인**. 아래 내용을 현재 시점의 확정된 정책으로 간주하고 작업을 진행합니다.
  1. **Local 탭 display_level: 현재는 백분율(percentage-based) 순위로 유지하고, 추후 최적화 방안을 논의합니다.
  2. **토픽 클러스터링**: LLM으로 토픽 제목을 생성/정제한 후, 해당 제목을 다시 임베딩하여 클러스터링 정확도를 높이는 방식을 고려합니다. (G의 데이터 파이프라인 설계에 반영)
  3. **커뮤니케이션**: 모든 에이전트는 요청/제안 시 대상을 **S(PO), C(개발), G(데이터/UX), O(인프라)**로 명확히 지정해야 합니다.
---

---

## 템플릿 (Template)
> 새 의사결정 제안(DT) 시 아래 템플릿을 복사하여 파일 최상단에 추가하세요.

```markdown
## DT-XXX: [제안 제목]

**제안자**: `C` | `G` | `O`
**날짜**: YYYY-MM-DD
**관련 TASK**: `TASK-XXX`, `TASK-YYY` (이 결정으로 인해 생성되거나 영향을 받는 WORK.md의 Task ID)

### 문제 (Problem)
- 

### 제안 (Proposal)
- 

### Reviews (다른 Agent 의견)
- **[G's Review]** YYYY-MM-DD:
  - ✅ **찬성/반대**: [의견]
  - ⚠️ **주의/우려**: [내용]
  - 📝 **추가 제안**: [내용]

### Final Decision by S
- 
---
```

## DT-001: [첫 번째 의사결정 제목, 예: MVP 기술 스택 선정]

**제안자**: [C, G, O 중]
**날짜**: YYYY-MM-DD
**관련 TASK**: `TASK-002`, `TASK-003`

### 문제 (Problem)
- MVP2 프로젝트의 프론트엔드, 백엔드, 인프라 기술 스택을 결정해야 합니다.

### 제안 (Proposal)
- **Frontend**: Next.js (React) on Vercel
- **Backend**: FastAPI (Python) on Cloud Run
- **Database**: Supabase (PostgreSQL)
- **CI/CD**: GitHub Actions

### Reviews (다른 Agent 의견)
- **[G's Review]** YYYY-MM-DD:
  - ✅ **찬성**. Python 백엔드는 데이터 파이프라인과의 연동이 용이합니다.
- **[O's Review]** YYYY-MM-DD:
  - ✅ **찬성**. Vercel과 GitHub Actions의 조합은 CI/CD 자동화에 효율적입니다.

### Final Decision by S
- **승인**. 제안된 기술 스택으로 MVP2 개발을 진행합니다.
