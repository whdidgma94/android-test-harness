# FastAPI web dashboard for android-test-harness
# Run: ANDROID_TEST_SESSION_DIR=.android-test-artifacts/{session-id} uvicorn gui.dashboard:app --port 8765

import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

app = FastAPI(title="Android Test Dashboard")


def get_session_dir() -> Path:
    env = os.environ.get("ANDROID_TEST_SESSION_DIR", "")
    return Path(env) if env else Path(".")


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


@app.get("/api/status")
def get_status():
    session_dir = get_session_dir()
    crawl_spec = read_json(session_dir / "crawl-spec.json", {})
    crawl_graph = read_json(session_dir / "crawl" / "crawl-graph.json", {})
    results_raw = read_json(session_dir / "execution" / "results.json", [])
    results = results_raw.get("cases", []) if isinstance(results_raw, dict) else results_raw

    nodes = crawl_graph.get("nodes", []) if isinstance(crawl_graph, dict) else []
    scenarios_dir = session_dir / "scenarios"
    scenario_count = len(list(scenarios_dir.glob("*.json"))) if scenarios_dir.exists() else 0

    pass_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "PASS")
    fail_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "FAIL")
    skip_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "SKIP")

    return {
        "package_name": crawl_spec.get("package_name", ""),
        "crawl_complete": (session_dir / "crawl" / "crawl-graph.json").exists(),
        "screen_count": len(nodes),
        "scenario_count": scenario_count,
        "test_results": {
            "pass": pass_count,
            "fail": fail_count,
            "skip": skip_count,
            "total": len(results),
        },
    }


@app.get("/api/screens")
def get_screens():
    session_dir = get_session_dir()
    crawl_graph = read_json(session_dir / "crawl" / "crawl-graph.json", {})
    return crawl_graph.get("nodes", []) if isinstance(crawl_graph, dict) else []


@app.get("/api/results")
def get_results():
    session_dir = get_session_dir()
    raw = read_json(session_dir / "execution" / "results.json", [])
    return raw.get("cases", []) if isinstance(raw, dict) else raw


@app.get("/screenshots/{screen_id}")
def get_screenshot(screen_id: str):
    session_dir = get_session_dir()
    img_path = session_dir / "crawl" / "screenshots" / f"{screen_id}.png"
    if img_path.exists():
        return FileResponse(str(img_path), media_type="image/png")
    raise HTTPException(status_code=404, detail="Screenshot not found")


_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>Android Test Dashboard</title>
<style>
*{box-sizing:border-box}
body{font-family:sans-serif;margin:0;padding:20px;background:#f0f2f5;color:#222}
h1{margin:0 0 16px;font-size:1.4em;color:#1565c0}
h2{margin:0 0 12px;font-size:1.05em;color:#333}
.card{background:#fff;padding:16px 20px;margin-bottom:14px;border-radius:10px;
      box-shadow:0 1px 4px rgba(0,0,0,.08)}
.stats{display:flex;gap:24px;flex-wrap:wrap;margin-top:8px}
.stat{text-align:center;min-width:60px}
.stat .num{font-size:2em;font-weight:700;line-height:1.1}
.stat .lbl{font-size:.75em;color:#666;margin-top:2px}
.pass .num{color:#2e7d32}.fail .num{color:#c62828}.skip .num{color:#e65100}
.blue .num{color:#1565c0}
.pkg{font-size:.9em;color:#555;margin-bottom:10px}
table{width:100%;border-collapse:collapse;font-size:.9em}
th{background:#e3f2fd;padding:8px 10px;text-align:left;font-weight:600;
   border-bottom:2px solid #90caf9}
td{padding:8px 10px;border-bottom:1px solid #eee;vertical-align:middle}
tr:last-child td{border-bottom:none}
.badge{display:inline-block;padding:2px 8px;border-radius:12px;font-size:.8em;font-weight:600}
.badge-pass{background:#e8f5e9;color:#2e7d32}
.badge-fail{background:#ffebee;color:#c62828}
.badge-skip{background:#fff3e0;color:#e65100}
.scr-img{width:90px;height:160px;object-fit:cover;border:1px solid #ddd;
         border-radius:4px;cursor:pointer;transition:transform .15s}
.scr-img:hover{transform:scale(1.05)}
.no-img{width:90px;height:160px;background:#f5f5f5;border:1px solid #ddd;
        border-radius:4px;display:flex;align-items:center;justify-content:center;
        font-size:.7em;color:#aaa;text-align:center}
#refresh-indicator{font-size:.75em;color:#999;float:right;margin-top:4px}
/* 모달 */
#modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);
       z-index:100;align-items:center;justify-content:center}
#modal.open{display:flex}
#modal img{max-width:90vw;max-height:90vh;border-radius:6px;box-shadow:0 4px 24px rgba(0,0,0,.5)}
#modal-close{position:fixed;top:16px;right:20px;color:#fff;font-size:2em;
             cursor:pointer;line-height:1;user-select:none}
</style>
</head>
<body>
<h1>Android Test Harness Dashboard
  <span id="refresh-indicator">자동 갱신: 대기 중</span>
</h1>

<div class="card" id="status-card"><p style="color:#999">데이터 로딩 중…</p></div>
<div class="card">
  <h2>탐색 화면 목록</h2>
  <div id="screens-area"><p style="color:#999">로딩 중…</p></div>
</div>
<div class="card">
  <h2>테스트 실행 결과</h2>
  <div id="results-area"><p style="color:#999">로딩 중…</p></div>
</div>

<!-- 스크린샷 확대 모달 -->
<div id="modal" onclick="closeModal()">
  <span id="modal-close">✕</span>
  <img id="modal-img" src="" alt="screenshot">
</div>

<script>
function openModal(src){ document.getElementById('modal-img').src=src; document.getElementById('modal').classList.add('open'); }
function closeModal(){ document.getElementById('modal').classList.remove('open'); }
document.addEventListener('keydown', e=>{ if(e.key==='Escape') closeModal(); });

function badge(status){
  const cls = status==='PASS'?'pass':status==='FAIL'?'fail':'skip';
  return `<span class="badge badge-${cls}">${status}</span>`;
}

let lastScreenCount = -1;

async function load() {
  try {
    const [s, sc, rs] = await Promise.all([
      fetch('/api/status').then(r=>r.json()),
      fetch('/api/screens').then(r=>r.json()),
      fetch('/api/results').then(r=>r.json()),
    ]);

    /* 상태 카드 */
    document.getElementById('status-card').innerHTML = `
      <div class="pkg"><b>패키지:</b> ${s.package_name||'-'}
        &nbsp;|&nbsp; <b>탐색:</b> ${s.crawl_complete?'완료 ✓':'진행 중'}</div>
      <div class="stats">
        <div class="stat blue"><div class="num">${s.screen_count}</div><div class="lbl">탐색 화면</div></div>
        <div class="stat blue"><div class="num">${s.scenario_count}</div><div class="lbl">시나리오</div></div>
        <div class="stat pass"><div class="num">${s.test_results.pass}</div><div class="lbl">PASS</div></div>
        <div class="stat fail"><div class="num">${s.test_results.fail}</div><div class="lbl">FAIL</div></div>
        <div class="stat skip"><div class="num">${s.test_results.skip}</div><div class="lbl">SKIP</div></div>
      </div>`;

    /* 화면 목록 — 화면 수가 바뀌었을 때만 다시 렌더 */
    if (sc.length !== lastScreenCount) {
      lastScreenCount = sc.length;
      const ts = Date.now();
      if (sc.length) {
        const rows = sc.map(n => {
          const sid = n.id || String(n);
          const src = `/screenshots/${sid}?t=${ts}`;
          const imgTag = sid
            ? `<img class="scr-img" src="${src}"
                   onclick="openModal('${src}')"
                   onerror="this.style.display='none';this.insertAdjacentHTML('afterend','<div class=\\'no-img\\'>이미지<br>없음</div>')">`
            : '<div class="no-img">-</div>';
          return `<tr>
            <td><code>${sid}</code></td>
            <td>${n.label||'-'}</td>
            <td style="font-size:.8em;color:#666">${n.activity||'-'}</td>
            <td>${imgTag}</td></tr>`;
        }).join('');
        document.getElementById('screens-area').innerHTML =
          `<table><tr><th>Screen ID</th><th>Label</th><th>Activity</th><th>Screenshot</th></tr>${rows}</table>`;
      } else {
        document.getElementById('screens-area').innerHTML = '<p style="color:#999">탐색 화면 없음</p>';
      }
    }

    /* 실행 결과 */
    if (rs.length) {
      const rows = rs.map(r => `<tr>
        <td><code>${r.id||'-'}</code></td>
        <td><code style="font-size:.8em;color:#666">${r.format||'-'}</code></td>
        <td>${badge(r.status||'SKIP')}</td>
        <td style="font-size:.8em;color:#555">${r.file||'-'}</td></tr>`).join('');
      document.getElementById('results-area').innerHTML =
        `<table><tr><th>ID</th><th>포맷</th><th>결과</th><th>파일</th></tr>${rows}</table>`;
    } else {
      document.getElementById('results-area').innerHTML = '<p style="color:#999">실행 결과 없음</p>';
    }

    document.getElementById('refresh-indicator').textContent =
      '자동 갱신: ' + new Date().toLocaleTimeString('ko-KR');
  } catch(e) {
    console.error(e);
    document.getElementById('refresh-indicator').textContent = '갱신 오류';
  }
}

load();
setInterval(load, 5000);   /* meta refresh 대신 JS 폴링 — 페이지 리로드 없음 */
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return _DASHBOARD_HTML


if __name__ == "__main__":
    import uvicorn
    session_dir = os.environ.get("ANDROID_TEST_SESSION_DIR", "")
    if not session_dir:
        print("환경변수 ANDROID_TEST_SESSION_DIR이 설정되지 않았습니다.")
        print("예: ANDROID_TEST_SESSION_DIR=.android-test-artifacts/20260526-155305-oneconnect uvicorn gui.dashboard:app --port 8765")
    uvicorn.run(app, host="0.0.0.0", port=8765)
