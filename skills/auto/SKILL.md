---
name: auto
description: 전체 파이프라인(intake → connect → crawl → testgen → execute → report)을 순차 오케스트레이션한다.
---

# auto skill

`orchestrator-agent`를 호출하여 전체 파이프라인을 실행한다.
파이프라인의 내부 절차(각 단계 수행 방법, 체크포인트 처리, 병렬 디스패치 등)는 `orchestrator-agent`가 정의하며, 이 파일에 중복 기술하지 않는다.

## 호출 방법

```
/auto "<대상 앱 설명>"
/auto "<대상 앱 설명>" --gui tui
/auto "<대상 앱 설명>" --gui web
/auto "<대상 앱 설명>" --gui none
```

- `<대상 앱 설명>`: 패키지명 또는 APK 경로, 탐색 범위, 원하는 테스트 케이스 포맷 등 자연어로 기술. 세션 종료 후 보존되지 않는 휘발성 정보.
- `--gui`: GUI 모드 선택 (`tui` / `web` / `none`). 생략 시 기본값 `web`.

## orchestrator-agent 전달 인자

| 인자 | 타입 | 설명 |
|------|------|------|
| `session-id` | `YYYYMMDD-HHmmss-{slug}` | 이 skill이 실행 시점에 생성하여 전달. 예: `20260526-110000-shopping-app`. |
| `user-request` | string (휘발성) | 사용자가 `/auto` 에 입력한 원문 그대로 전달. 파일 경로나 패키지명 포함. |
| `gui-mode` | `tui` \| `web` \| `none` | `--gui` 옵션 값. 생략 시 `web`. |

> 세 가지 인자 외에 다른 컨텍스트(파일 내용, 이전 단계 출력 등)를 프롬프트에 포함하지 않는다.
> orchestrator-agent는 `session-id`를 통해 `.android-test-artifacts/{session-id}/` 경로를 직접 구성하고 필요한 파일을 Read한다.

## 입출력

| 항목 | 설명 |
|------|------|
| **입력** | 사용자 자연어 요청 (대상 앱 정보 포함), gui-mode 옵션 |
| **session-id 생성** | skill이 `YYYYMMDD-HHmmss-{slug}` 형식으로 생성 후 orchestrator-agent에 전달 |
| **출력** | `.android-test-artifacts/{session-id}/` 하위 전체 산출물 (crawl-spec.json, crawl-graph.json, 테스트 케이스 파일, final-report.md, README.md 등) |

## 실행 흐름 요약

```
/auto "요청"
  └─► orchestrator-agent (session-id, user-request, gui-mode)
        └─► [파이프라인 전체 수행 — 상세는 orchestrator-agent 참조]
```

파이프라인 완료 후 orchestrator-agent가 최종 산출물 경로와 요약을 터미널에 출력한다.

## 중단 및 재실행

- 중간에 중단된 경우 동일 `session-id`로 orchestrator-agent를 재호출할 수 없다. 새 `session-id`로 `/auto`를 재실행한다.
- GUI 프로세스가 잔존하는 경우 `/gui-up stop` 커맨드로 정리한다.
