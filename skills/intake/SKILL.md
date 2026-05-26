---
name: intake
description: 사용자 요청을 수집하여 crawl-spec.json을 생성한다. 전체 파이프라인의 첫 단계.
---

# intake skill

`intake-agent`를 호출하여 사용자의 자연어 요청과 대상 앱 정보를 받아 `crawl-spec.json`을 생성한다.

## 호출 방법

```
/intake "요청"
```

## intake-agent 전달 인자

| 인자 | 필수 여부 | 설명 |
|------|-----------|------|
| `session-id` | 필수 | `YYYYMMDD-HHmmss-{slug}` 형식 (예: `20260526-110000-shopping-app`). skill이 호출 시점에 생성하여 전달한다. |
| 자연어 요청 | 필수 | 사용자가 `/intake` 커맨드에 전달한 원문 텍스트. 휘발성 인자이므로 파일에 저장하지 않고 직접 전달한다. |
| `package_name` | 조건부 | 대상 앱의 안드로이드 패키지명 (예: `com.example.app`). `apk_path`가 없을 경우 필수. |
| `apk_path` | 조건부 | APK 파일 경로. 제공 시 `adb install -r`로 자동 설치된다. `package_name`과 함께 제공 가능. |
| `formats` | 선택 | 생성할 테스트 케이스 포맷 목록. `gherkin`, `pytest`, `junit` 중 복수 선택 가능. 기본값: 전체 선택. |
| `gui_mode` | 선택 | GUI 대시보드 종류. `tui`, `web`, `none` 중 하나. 기본값: `web`. |

> 파일 내용(crawl-spec.json 등)은 인자로 전달하지 않는다. intake-agent는 session-id를 기반으로 경로를 직접 계산하여 파일을 읽고 쓴다.

## 산출물

```
.android-test-artifacts/{session-id}/crawl-spec.json
```

`crawl-spec.json`이 생성되면 intake 단계가 완료된다. 이후 단계(connect)는 이 파일을 직접 읽어 동작한다.
