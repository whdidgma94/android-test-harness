---
name: connect
description: ADB/Appium 연결 점검, 디바이스 선택, 체크포인트 #1(자동 조작 승인)을 실행한다.
---

# connect skill

`device-connector-agent`를 호출하여 ADB/Appium 연결 점검, 디바이스 선택, 체크포인트 #1을 수행한다.

## 호출 방법

```
Task(
  description="device-connector-agent 실행",
  prompt="device-connector-agent를 실행한다.\nsession-id: {session-id}",
  subagent_type="device-connector-agent",
  subagent_model="claude-opus-4-7"
)
```

전달 인자는 `session-id` 하나만 넘긴다. 나머지 컨텍스트(대상 패키지명, APK 경로, 탐색 범위, GUI 모드 등)는 agent가 `.android-test-artifacts/{session-id}/crawl-spec.json`을 직접 읽어 취득한다.

## 전달 인자

| 인자 | 타입 | 설명 |
|------|------|------|
| `session-id` | string | 현재 세션 식별자. 형식: `YYYYMMDD-HHmmss-{slug}` |

## 산출물

| 경로 | 설명 |
|------|------|
| `.android-test-artifacts/{session-id}/device-info.json` | 선택된 디바이스 정보 및 Appium/ADB 연결 상태 |

## 체크포인트 #1

`device-connector-agent`가 완료 보고를 올리면 사용자에게 자동 조작 시작 승인을 요청한다. 사용자가 승인해야 다음 단계(`crawl`)로 진행한다. 승인 거부 시 파이프라인을 중단한다.
