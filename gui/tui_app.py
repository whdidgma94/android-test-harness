# Textual TUI dashboard for android-test-harness
# Run: python gui/tui_app.py .android-test-artifacts/{session-id}

import json
import sys
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header, Static


def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


class AndroidTestDashboard(App):
    CSS = """
    Screen { background: $surface; }
    #stats { height: 3; background: $panel; padding: 0 2; content-align: left middle; }
    #screens { height: 1fr; }
    #results { height: 1fr; }
    """
    TITLE = "Android Test Harness"

    def __init__(self, session_dir: Path) -> None:
        super().__init__()
        self.session_dir = session_dir

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Loading...", id="stats")
        yield DataTable(id="screens")
        yield DataTable(id="results")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#screens", DataTable).add_columns("Screen ID", "Label", "Activity")
        self.query_one("#results", DataTable).add_columns("Scenario", "Status", "Message")
        self.set_interval(1.0, self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        crawl_spec = _read_json(self.session_dir / "crawl-spec.json", {})
        crawl_graph = _read_json(self.session_dir / "crawl" / "crawl-graph.json", {})
        results = _read_json(self.session_dir / "execution" / "results.json", [])

        nodes = crawl_graph.get("nodes", []) if isinstance(crawl_graph, dict) else []
        scenarios_dir = self.session_dir / "scenarios"
        scenario_count = len(list(scenarios_dir.glob("*.json"))) if scenarios_dir.exists() else 0

        pass_c = sum(1 for r in results if r.get("status") == "PASS")
        fail_c = sum(1 for r in results if r.get("status") == "FAIL")
        skip_c = sum(1 for r in results if r.get("status") == "SKIP")

        pkg = crawl_spec.get("package_name", self.session_dir.name)
        self.sub_title = pkg
        self.query_one("#stats", Static).update(
            f"패키지: {pkg}  |  화면: {len(nodes)}  |  시나리오: {scenario_count}  |  "
            f"PASS: {pass_c}  FAIL: {fail_c}  SKIP: {skip_c}"
        )

        screens_table = self.query_one("#screens", DataTable)
        screens_table.clear()
        for s in nodes:
            if isinstance(s, dict):
                screens_table.add_row(s.get("id", "-"), s.get("label", "-"), s.get("activity", "-"))
            else:
                screens_table.add_row(str(s), "-", "-")

        results_table = self.query_one("#results", DataTable)
        results_table.clear()
        for r in results:
            results_table.add_row(
                r.get("scenario_id", r.get("id", "-")),
                r.get("status", "-"),
                (r.get("message") or "-")[:60],
            )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python gui/tui_app.py <session-dir>")
        print("예: python gui/tui_app.py .android-test-artifacts/20260526-155305-oneconnect")
        sys.exit(1)
    AndroidTestDashboard(Path(sys.argv[1])).run()
