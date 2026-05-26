# android-test-harness

ADB로 연결된 안드로이드 디바이스/에뮬레이터의 앱을 자동 탐색하고, Gherkin / pytest+Appium / JUnit5 테스트 케이스를 자동 생성·실행하는 Claude Code 하네스.

## 파이프라인 흐름

```
/auto "요청"
     │
     ▼
 ┌─────────┐
 │  intake  │  자연어 요청 → crawl-spec.json 생성
 └────┬─────┘
      │
      ▼
 ┌─────────┐
 │ connect  │  ADB/Appium 점검 + 디바이스 선택
 └────┬─────┘
      │  [체크포인트 #1: 자동 조작 시작 전 사용자 승인]
      ▼
 ┌─────────┐
 │  crawl   │  BFS로 앱 화면 탐색 (XML + 스크린샷 저장)
 └────┬─────┘
      │
      ▼
 ┌─────────┐
 │ testgen  │  시나리오별 병렬 케이스 생성 (Gherkin / pytest / JUnit)
 └────┬─────┘
      │  [체크포인트 #2: 실행 전 사용자 승인]
      ▼
 ┌─────────┐
 │ execute  │  pytest 실행 + 결과 수집 (JUnit은 파일 생성만)
 └────┬─────┘
      │
      ▼
 ┌─────────┐
 │  report  │  final-report.md + final-report.html + README 생성
 └─────────┘
```

## 시작하기

```bash
# 레포 클론
git clone <repo-url>
cd android-test-harness

# 의존성 설치
pip install uiautomator2 pytest textual fastapi uvicorn

# 디바이스 연결 확인
adb devices

# 전체 파이프라인 실행 (Claude Code에서)
/auto "com.example.myapp 앱의 로그인 및 메인 화면을 탐색하고 테스트 케이스를 생성해줘"
```

## 커맨드

| 커맨드 | 설명 |
|--------|------|
| `/auto "요청"` | 전체 파이프라인 실행 (가장 일반적인 진입점) |
| `/intake "요청"` | crawl-spec.json만 생성 (탐색 범위 확인용) |
| `/connect` | ADB/Appium 연결 점검 및 디바이스 선택 |
| `/crawl` | 앱 화면 BFS 탐색 실행 |
| `/testgen` | 탐색 결과 기반 테스트 케이스 병렬 생성 |
| `/execute` | 생성된 케이스를 디바이스에서 실행 |
| `/report` | 최종 리포트 생성 |
| `/gui-up [tui\|web]` | GUI 대시보드 별도 기동 |

## 지원 테스트 포맷

| 포맷 | 파일 | 실행 여부 |
|------|------|-----------|
| Gherkin | `tests/gherkin/{scenario-id}.feature` | 파일 생성만 (BDD 러너 별도 필요) |
| pytest + Appium | `tests/pytest/{scenario-id}.py` | execute 단계에서 자동 실행 |
| JUnit5 + UIAutomator2 | `tests/junit/{scenario-id}.java` | 파일 생성만 (Gradle 프로젝트 필요) |

intake 시 포맷을 multi-select로 선택하며, 기본값은 세 가지 모두 생성한다.

## GUI 모드

| 모드 | 실행 방법 | 접속 |
|------|-----------|------|
| `web` (기본값) | `crawl-spec.json`에 `"gui_mode": "web"` | 브라우저 `http://localhost:8000` |
| `tui` | `"gui_mode": "tui"` | 현재 터미널 (Textual TUI) |
| `none` | `"gui_mode": "none"` | CLI 로그만 출력 |

GUI 프로세스 종료: `/gui-up stop` 또는 `gui/gui.pid` 파일의 PID를 kill.

## 외부 의존성

| 도구 | 설치 | 용도 |
|------|------|------|
| ADB (Android SDK Platform-Tools) | [developer.android.com/tools/releases/platform-tools](https://developer.android.com/tools/releases/platform-tools) | 디바이스 연결, 앱 조작 필수 |
| Python 3.10+ | [python.org](https://python.org) | 탐색 스크립트 및 pytest 실행 |
| uiautomator2 | `pip install uiautomator2` | 앱 화면 탐색 (필수) |
| pytest | `pip install pytest` | 테스트 실행 |
| textual | `pip install textual` | TUI 대시보드 (tui 모드만) |
| fastapi + uvicorn | `pip install fastapi uvicorn` | 웹 대시보드 (web 모드만) |
| Appium (선택) | `npm i -g appium && appium driver install uiautomator2` | uiautomator2 폴백 또는 크로스 플랫폼 |

ADB 미설치 시 파이프라인 중단. Appium 미설치 시 uiautomator2-only 모드로 자동 전환.

## 산출물 경로

```
.android-test-artifacts/
└── {YYYYMMDD-HHmmss-slug}/
    ├── crawl-spec.json
    ├── device-info.json
    ├── crawl/
    │   ├── crawl-graph.json
    │   ├── screens/scr-{hex}.xml
    │   ├── screenshots/scr-{hex}.png
    │   └── crawl-log.md
    ├── scenarios/sc-{nnn}.json
    ├── tests/
    │   ├── gherkin/sc-{nnn}.feature
    │   ├── pytest/sc-{nnn}.py
    │   └── junit/sc-{nnn}.java
    ├── execution/
    │   ├── results.json          # PASS / FAIL / SKIP
    │   ├── logs/sc-{nnn}.log
    │   └── failures/sc-{nnn}.png
    ├── gui/
    │   ├── gui.pid
    │   └── gui.log
    ├── final-report.md
    ├── final-report.html
    └── README.md
```

세션 디렉토리는 실행마다 독립 생성되므로 여러 세션을 동시에 운영할 수 있다.

## Agent 구성

| Agent | 역할 | 모델 |
|-------|------|------|
| orchestrator-agent | 전체 파이프라인 진행, 체크포인트 관리, 병렬 worker 디스패치 | Opus |
| intake-agent | 자연어 요청 → crawl-spec.json 생성 | Opus |
| device-connector-agent | ADB/Appium 점검, 디바이스 선택 | Opus |
| app-crawler-agent | BFS 탐색 실행, crawl-graph.json 산출 | Sonnet |
| test-generator-agent | 시나리오 1개 → 케이스 파일 생성 (병렬 호출) | Sonnet |
| test-runner-agent | pytest 실행, 결과 수집 | Sonnet |
| report-writer-agent | 최종 리포트 및 README 생성 | Sonnet |
| gui-launcher-agent | TUI/웹 대시보드 프로세스 관리 | Haiku |
