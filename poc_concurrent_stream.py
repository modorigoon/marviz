"""PoC: Textual에서 여러 async worker가 동시에 각각 다른 패널에 스트리밍 출력.

검증 목표:
1. @work(exclusive=True) — 메인 에이전트용 (새 입력 시 이전 스트림 취소)
2. @work (non-exclusive) — 서브 에이전트용 (병렬 실행)
3. 각 worker가 자기 패널의 RichLog에 실시간으로 토큰을 쓸 수 있는가
4. 메인에서 서브를 동적으로 생성할 수 있는가

실행: python poc_concurrent_stream.py
"""

import asyncio

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, RichLog, Static


# ── Fake LLM stream (API 키 없이 테스트) ──
async def fake_llm_stream(prompt: str, agent_name: str, speed: float = 0.05):
    """LiteLLM acompletion(stream=True)를 시뮬레이션."""
    words = f"{agent_name} is processing: {prompt}".split()
    for word in words:
        await asyncio.sleep(speed)
        yield word + " "
    # 메인 에이전트에서 "spawn" 입력 시 tool_use 시뮬레이션
    if agent_name == "Main" and "spawn" in prompt.lower():
        yield "\n__TOOL_USE:spawn__\n"


class PoCApp(App):
    CSS = """
    Screen { background: #000080; }
    #main-area { height: 1fr; }
    .panel {
        border: double #00aaaa;
        background: #000080;
        height: 1fr;
    }
    .panel RichLog {
        background: #000080;
        color: #aaaaaa;
        height: 1fr;
    }
    #main-panel { width: 1fr; }
    #sub-area { width: 2fr; }
    Input {
        dock: bottom;
        background: #000080;
        color: #ffffff;
        border: none;
    }
    .sub-panel {
        height: 1fr;
        border-bottom: solid #005555;
        background: #000080;
        color: #aaaaaa;
    }
    #status {
        dock: bottom;
        height: 1;
        background: black;
        color: #ffff55;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="main-area"):
            with Vertical(id="main-panel", classes="panel"):
                yield RichLog(id="main-log", highlight=True, markup=True)
                yield Input(placeholder="> ", id="main-input")
            with Vertical(id="sub-area", classes="panel"):
                yield RichLog(id="sub-1", classes="sub-panel", highlight=True, markup=True)
                yield RichLog(id="sub-2", classes="sub-panel", highlight=True, markup=True)
                yield RichLog(id="sub-3", classes="sub-panel", highlight=True, markup=True)
        yield Static("Workers: 0 active", id="status")

    def on_mount(self) -> None:
        self.query_one("#main-panel").border_title = " Main Agent "
        self.query_one("#sub-area").border_title = " Sub-Agents "
        main_log = self.query_one("#main-log", RichLog)
        main_log.write("[b]PoC: Concurrent Streaming[/b]")
        main_log.write("Type any message, or type 'spawn' to create sub-agents.")
        main_log.write("")
        for i in range(1, 4):
            self.query_one(f"#sub-{i}", RichLog).write(f"[dim]Worker-{i} idle[/dim]")
        self._active_workers = 0

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "main-input":
            return
        text = event.value.strip()
        if not text:
            return
        event.input.clear()
        self.query_one("#main-log", RichLog).write(f"[#55ff55]> {text}[/]")
        self._stream_main(text)

    @work(exclusive=True, group="main")
    async def _stream_main(self, prompt: str) -> None:
        """메인 에이전트: exclusive (새 입력 시 이전 취소)."""
        log = self.query_one("#main-log", RichLog)
        self._active_workers += 1
        self._update_status()

        spawn_detected = False
        async for token in fake_llm_stream(prompt, "Main", speed=0.08):
            if "__TOOL_USE:" in token:
                spawn_detected = True
                continue
            log.write(f"[#aaaaaa]{token}[/]", scroll_end=True)

        log.write("")
        self._active_workers -= 1
        self._update_status()

        if spawn_detected:
            log.write("[#ffff55]-> Spawning 3 sub-agents...[/]")
            for i in range(1, 4):
                self._stream_sub(f"Sub-task {i} from: {prompt}", i)

    @work(exclusive=False, group="sub")
    async def _stream_sub(self, task: str, agent_id: int) -> None:
        """서브 에이전트: non-exclusive (병렬 실행)."""
        log = self.query_one(f"#sub-{agent_id}", RichLog)
        log.clear()
        log.write(f"[#00aaaa]Worker-{agent_id} started[/]")
        self._active_workers += 1
        self._update_status()

        speed = 0.05 + (agent_id * 0.03)
        async for token in fake_llm_stream(task, f"Worker-{agent_id}", speed):
            if "__TOOL_USE:" in token:
                continue
            log.write(f"{token}", scroll_end=True)

        log.write(f"\n[#55ff55]Worker-{agent_id} done[/]")
        self._active_workers -= 1
        self._update_status()

    def _update_status(self) -> None:
        self.query_one("#status", Static).update(
            f"Workers: {self._active_workers} active"
        )


if __name__ == "__main__":
    PoCApp().run()
