---
name: gui-up
description: GUI 대시보드(TUI 또는 웹)를 독립적으로 시작하거나 종료한다. auto skill과 별도로 호출 가능.
---

# gui-up

`gui-launcher-agent`를 호출하여 GUI 대시보드 프로세스를 시작하거나 종료한다.

## 호출 방법

```
/gui-up [tui|web|stop]
```

## 전달 인자

`gui-launcher-agent`에 아래 두 인자만 전달한다.

| 인자 | 값 | 설명 |
|------|----|------|
| `session-id` | `YYYYMMDD-HHmmss-{slug}` | 현재 세션 ID. `.android-test-artifacts/` 하위 작업 디렉토리를 특정한다. |
| `gui-mode` | `tui` \| `web` \| `stop` | `tui`: Textual TUI 시작, `web`: FastAPI 웹 대시보드 시작, `stop`: 실행 중인 GUI 프로세스 종료. |

## 산출물

| 파일 | 설명 |
|------|------|
| `.android-test-artifacts/{session-id}/gui/gui.pid` | 백그라운드 GUI 프로세스 PID |
| `.android-test-artifacts/{session-id}/gui/gui.log` | GUI 프로세스 실행/종료 로그 |
