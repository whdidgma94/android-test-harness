---
name: execute
description: 생성된 테스트 케이스를 디바이스에서 실행하고 결과를 기록한다. 체크포인트 #2(실행 승인) 포함.
---

# execute skill

`test-runner-agent`를 호출하여 생성된 테스트 케이스를 디바이스에서 실행한다.

## 호출 방법

```
/execute
```

`session-id`는 현재 세션 컨텍스트에서 자동으로 전달된다. skill은 `session-id` 외에 추가 인자를 전달하지 않는다.

## 전달 인자

| 인자 | 설명 |
|------|------|
| `session-id` | 실행 대상 세션 식별자 (`YYYYMMDD-HHmmss-{slug}` 형식) |

agent는 나머지 컨텍스트(케이스 목록, 디바이스 정보, 포맷 설정 등)를 세션 디렉토리 내 파일에서 직접 읽는다.

## 체크포인트 #2

`test-runner-agent` 실행 시작 전, 사용자에게 실행 승인을 요청한다. 승인이 거부되면 파이프라인을 중단한다. 체크포인트의 구체적인 안내 내용(케이스 목록, 디바이스 상태 변경 경고 등)은 agent가 담당한다.

## 산출물

| 경로 | 설명 |
|------|------|
| `execution/results.json` | 케이스별 `PASS / FAIL / SKIP` 판정 결과 |
| `execution/logs/{scenario-id}.log` | 시나리오별 실행 로그 |
| `execution/failures/{scenario-id}.png` | 실패 케이스 스크린샷 |

> 판정 라벨은 `PASS / FAIL / SKIP` 3종으로 고정한다. 다른 라벨은 사용하지 않는다.
