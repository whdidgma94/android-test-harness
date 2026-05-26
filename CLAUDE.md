# android-test-harness

ADB로 연결된 안드로이드 디바이스/에뮬레이터의 앱을 자동 탐색하고, UI 요소 기반 테스트 케이스를 자동 생성·실행하는 하네스.

## 사전 요구사항

### 필수
- **ADB**: Android SDK Platform-Tools 설치 후 `adb devices`로 디바이스/에뮬레이터 인식 확인
- **Python 3.10+**: 아래 패키지 설치 필요
  ```bash
  pip install uiautomator2 pytest textual fastapi uvicorn
  ```

### 선택
- **Appium**: uiautomator2 드라이버와 함께 설치 시 Appium 모드 활성화
  ```bash
  npm i -g appium
  appium driver install uiautomator2
  ```
- **JUnit5**: 생성된 `.java` 케이스 파일은 참고용이며, execute 단계에서 SKIP된다. 실제 실행은 별도 안드로이드 프로젝트(Gradle) 환경이 필요하다.

## 산출물 경로

모든 산출물은 `.android-test-artifacts/{session-id}/` 하위에 격리 저장된다.
`{session-id}` 형식: `YYYYMMDD-HHmmss-{slug}` (예: `20260526-110000-shopping-app`)

```
.android-test-artifacts/{session-id}/
├── crawl-spec.json              # 대상 앱, 탐색 범위, 케이스 포맷, GUI 모드
├── device-info.json             # 선택된 디바이스 및 Appium 정보
├── crawl/
│   ├── crawl-graph.json         # 화면 그래프 (노드: screen-id, 엣지: action)
│   ├── screens/{screen-id}.xml  # 화면별 UI hierarchy
│   ├── screenshots/{screen-id}.png
│   └── crawl-log.md
├── scenarios/
│   └── {scenario-id}.json       # testgen 입력용 시나리오 정의
├── tests/
│   ├── gherkin/{scenario-id}.feature
│   ├── pytest/{scenario-id}.py
│   └── junit/{scenario-id}.java
├── execution/
│   ├── results.json             # 케이스별 PASS/FAIL/SKIP
│   ├── logs/{scenario-id}.log
│   └── failures/{scenario-id}.png
├── gui/
│   ├── gui.pid                  # 백그라운드 GUI 프로세스 PID
│   └── gui.log
├── final-report.md
├── final-report.html
└── README.md                    # 산출물 사용 가이드
```

**ID 형식**
- `screen-id`: `scr-{4자리 hex}` (예: `scr-0a1b`)
- `scenario-id`: `sc-{3자리 zero-pad}` (예: `sc-001`)
- 테스트 결과 라벨: `PASS / FAIL / SKIP` (3종 고정)
- 탐색 완료 판정: `COMPLETE / PARTIAL / ABORTED`

## 파이프라인 규칙

1. **쓰기 범위 제한**: 모든 agent의 Write/Edit는 `.android-test-artifacts/{session-id}/` 하위로 제한한다. 사용자의 안드로이드 프로젝트나 시스템 파일에 직접 쓰지 않는다.
2. **agent 격리 원칙**: skill은 sub-agent에게 `session-id`와 휘발성 인자(예: `scenario-id`, `gui-mode`)만 전달한다. agent는 `crawl-spec.json` 등 컨텍스트를 파일에서 직접 읽는다.
3. **모델 배정 강제**: 설계·판단 단계(orchestrator, intake, device-connector) = Opus, 구현·실행 단계(crawler, test-generator, test-runner, report-writer) = Sonnet, 단순 프로세스 관리(gui-launcher) = Haiku.
4. **사용자 체크포인트**:
   - **체크포인트 #1 (connect 직후)**: 자동 조작 시작 전 디바이스/패키지/탐색 범위를 사용자에게 보여주고 명시적 승인을 받는다.
   - **체크포인트 #2 (execute 직전)**: 생성된 테스트 케이스 목록과 실행 시 변경 가능한 디바이스 상태(데이터 삭제, 로그인 흐름 등)를 안내하고 승인을 받는다.
5. **외부 도구 폴백**:
   - `which adb` 실패 → 설치 가이드 출력 후 파이프라인 중단.
   - `which appium` 실패 → uiautomator2-only 모드로 자동 전환.
   - `python -c "import uiautomator2"` 실패 → 설치 명령 안내 후 중단.
   - `gui-mode: none` 시 gui-launcher-agent는 호출되지 않는다.
6. **병렬 실행**: testgen 단계에서 시나리오별 `test-generator-agent`를 병렬 호출한다. 병렬 시작 전에 orchestrator-agent가 `tests/gherkin/`, `tests/pytest/`, `tests/junit/`, `scenarios/` 디렉토리를 사전 생성한다.
7. **GUI 백그라운드 프로세스 수명관리**: gui-launcher-agent는 PID를 `gui/gui.pid`에 기록한다. 파이프라인 종료 시 orchestrator-agent가 PID를 읽어 종료 처리한다.
8. **재현성**: 모든 산출물은 `session-id` 디렉토리에 격리되어 여러 세션을 동시에 운영할 수 있다.
9. **탐색 상한 기본값**: `max_depth: 15`, `max_screens: 500`, `max_minutes: 60`.
10. **앱 설치**: `apk_path` 지정 시 `adb install -r`로 자동 설치, 미지정 시 기존 설치된 패키지를 사용한다.

## 커맨드

| 커맨드 | 설명 |
|--------|------|
| `/auto "요청"` | 전체 파이프라인(intake → connect → crawl → testgen → execute → report) 순차 실행 |
| `/intake "요청"` | 자연어 요청을 분석하여 `crawl-spec.json` 생성 |
| `/connect` | ADB/Appium 점검, 디바이스 선택, 체크포인트 #1 안내 |
| `/crawl` | UIAutomator2/Appium으로 앱 화면 BFS 탐색 |
| `/testgen` | 탐색 결과를 분석하여 테스트 케이스 파일 병렬 생성 |
| `/execute` | 생성된 테스트 케이스를 디바이스에서 실행 (체크포인트 #2 포함) |
| `/report` | 탐색·실행 결과를 취합하여 최종 리포트 생성 |
| `/gui-up [tui\|web]` | GUI 대시보드만 별도로 기동 |

## GUI 모드

| 모드 | 설명 |
|------|------|
| `tui` | Textual 기반 터미널 TUI. 추가 브라우저 없이 터미널에서 실시간 진행 확인 |
| `web` | FastAPI + HTML 웹 대시보드 (기본값). 브라우저에서 `http://localhost:8000` 접속 |
| `none` | GUI 없이 CLI 로그만 출력. gui-launcher-agent 미호출 |

GUI 프로세스 종료:
- `/gui-up stop` 커맨드 실행
- 또는 `.android-test-artifacts/{session-id}/gui/gui.pid`의 PID를 직접 kill

## 외부 의존성 폴백

| 도구 | 미설치 시 동작 |
|------|--------------|
| ADB | 설치 가이드 출력 후 파이프라인 중단 |
| Appium | uiautomator2-only 모드로 자동 전환 (uiautomator2 설치 전제) |
| uiautomator2 (Python) | `pip install uiautomator2` 안내 후 중단 |
| textual / fastapi / uvicorn | `pip install` 안내 후 중단 (GUI 모드 사용 시만 해당) |

## 참조 문서

- `docs/test-templates/` — Gherkin feature, pytest+Appium, JUnit5 케이스 템플릿
