---
name: crawl
description: UIAutomator2/Appium으로 앱 화면을 BFS 탐색하고 crawl-graph.json을 산출한다.
---

# crawl skill

`app-crawler-agent`를 호출하여 BFS 탐색을 수행한다.

## 호출 방법

`app-crawler-agent`에 아래 인자 하나만 전달한다.

| 인자 | 설명 |
|------|------|
| `session-id` | 현재 세션 식별자. 형식: `YYYYMMDD-HHmmss-{slug}` |

agent는 `.android-test-artifacts/{session-id}/crawl-spec.json` 및 `device-info.json`을 직접 읽어 탐색을 수행한다. skill 프롬프트에 파일 내용을 포함하지 않는다.

## 산출물

`app-crawler-agent` 완료 후 아래 경로에 파일이 생성된다.

```
.android-test-artifacts/{session-id}/
└── crawl/
    ├── crawl-graph.json          # 화면 그래프 (노드: screen-id, 엣지: action)
    ├── screens/{screen-id}.xml   # 화면별 UI hierarchy
    ├── screenshots/{screen-id}.png
    └── crawl-log.md
```

## GUI 백그라운드 프로세스

`/connect` 이후 GUI 모드가 활성화된 경우(`gui-mode: tui` 또는 `web`), GUI 프로세스는 이미 백그라운드에서 실행 중이다. crawl skill은 GUI 프로세스를 별도로 기동하거나 종료하지 않는다.
