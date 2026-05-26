---
name: report
description: 탐색·테스트 결과 전체를 취합하여 최종 리포트와 README를 생성한다.
---

# report skill

`report-writer-agent`를 호출하여 세션의 모든 산출물을 취합하고 최종 리포트를 생성한다.

## 호출 방법

```
Task report-writer-agent with session-id: {session-id}
```

`session-id`만 전달한다. agent는 `.android-test-artifacts/{session-id}/` 하위 파일을 직접 읽어 필요한 컨텍스트를 수집한다.

## 산출물

agent 완료 후 아래 파일이 `.android-test-artifacts/{session-id}/` 에 생성된다.

| 파일 | 설명 |
|------|------|
| `final-report.md` | 탐색 결과·테스트 결과·생성 케이스 취합 리포트 (Markdown) |
| `final-report.html` | 동일 내용의 HTML 포맷 리포트 |
| `README.md` | 산출물 사용 가이드 (케이스 위치, 재실행 방법) |

## 실행 예시

```
/report
```

`session-id`는 현재 세션에서 자동으로 결정된다. 명시적으로 지정할 경우:

```
/report 20260526-110000-shopping-app
```
