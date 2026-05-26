---
name: testgen
description: 탐색 기록(crawl-graph.json)을 분석하여 시나리오별 테스트 케이스 파일을 병렬 생성한다.
---

## 호출 방법

`session-id`를 인자로 orchestrator-agent를 호출한다.

```
orchestrator-agent에게 전달:
  session-id: <session-id>
```

orchestrator-agent가 `session-id`를 받아 `crawl-graph.json`과 `scenarios/`를 읽고,
시나리오별로 `test-generator-agent`를 병렬 호출한다.
내부 절차(디렉토리 사전 생성, 시나리오 파티셔닝 방법 등)는 orchestrator-agent 파일에 정의되어 있다.

## 산출물

시나리오 ID 형식은 `sc-{3자리 zero-pad}` (예: `sc-001`, `sc-042`).

| 파일 | 경로 |
|------|------|
| 시나리오 정의 | `.android-test-artifacts/{session-id}/scenarios/{sc-xxx}.json` |
| Gherkin | `.android-test-artifacts/{session-id}/tests/gherkin/{sc-xxx}.feature` |
| pytest+Appium | `.android-test-artifacts/{session-id}/tests/pytest/{sc-xxx}.py` |
| JUnit5 | `.android-test-artifacts/{session-id}/tests/junit/{sc-xxx}.java` |
