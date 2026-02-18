from __future__ import annotations

import uuid
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual import work

from textual.widgets import DirectoryTree

from ...agents.main_agent import MainAgent
from ...agents.sub_agent import SubAgent
from ...agents.types import AccumulatedToolCall
from ...config import MarvizConfig
from ...providers.litellm_provider import LiteLLMProvider
from ..messages import SubAgentCompleted, UserMessage
from ..widgets import (
    AgentContainer,
    ChatPanel,
    CodeEditorPanel,
    FileTreePanel,
    FKeyBar,
    StatusBar,
    TerminalPanel,
    TitleBar,
)

# Tools that are executed immediately (no sub-agent needed)
_IMMEDIATE_TOOLS = {"write_file", "read_file"}


class MainScreen(Screen):
    """MDIR-style main screen with sub-agent orchestration.

    +===========+==================+===========+
    |           |  Worker-1        | Files     |
    |  Main     |------------------|-----------|
    |  Agent    |  Worker-2        | Editor    |
    |  (Chat)   |------------------|           |
    |           |  Worker-3        |           |
    +===========+==================+===========+
    |  Status                      | Terminal  |
    +==============================+===========+
    1Help 2Chat 3View 4Edit 5Agent 6Model 7Term 8Tree 9Conf 10Quit
    """

    BINDINGS = [
        ("f1", "help", "Help"),
        ("f2", "focus_chat", "Chat"),
        ("f7", "focus_terminal", "Term"),
        ("f8", "focus_tree", "Tree"),
        ("f10", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield TitleBar()
        with Vertical(id="app-body"):
            with Horizontal(id="main-area"):
                yield ChatPanel(id="chat-panel")
                yield AgentContainer(id="agent-container")
                with Vertical(id="right-column"):
                    yield FileTreePanel(id="file-tree-panel")
                    yield CodeEditorPanel(id="code-editor-panel")
            with Horizontal(id="bottom-row"):
                yield StatusBar()
                yield TerminalPanel(id="terminal-panel")
        yield FKeyBar()

    def on_mount(self) -> None:
        config = MarvizConfig.load()
        self._provider = LiteLLMProvider(config.default_model)
        self.main_agent = MainAgent(self._provider)
        self._pending_results: dict[str, str] = {}  # tool_call_id -> result
        self._expected_tool_calls: list[AccumulatedToolCall] = []

        status = self.query_one(StatusBar)
        status.update_model(config.default_model)

        if not MarvizConfig.has_api_key():
            chat = self.query_one("#chat-panel", ChatPanel)
            chat.show_error(
                "No API key found. Set ANTHROPIC_API_KEY (or other provider key) in .env"
            )

    def on_user_message(self, event: UserMessage) -> None:
        chat = self.query_one("#chat-panel", ChatPanel)
        chat.show_user_message(event.text)
        self._run_agent(event.text)

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Open the selected file in the editor panel."""
        editor = self.query_one("#code-editor-panel", CodeEditorPanel)
        editor.open_file(event.path)

    # ── Main agent ──

    @work(exclusive=True, group="main-agent")
    async def _run_agent(self, text: str) -> None:
        chat = self.query_one("#chat-panel", ChatPanel)
        status = self.query_one(StatusBar)

        status.update_status("Thinking...")
        token_count = 0

        async for chunk in self.main_agent.send(text):
            if chunk.type == "text":
                chat.append_token(chunk.content)
                token_count += len(chunk.content) // 4
            elif chunk.type == "error":
                chat.show_error(chunk.content)

        chat.finish_response()
        status.update_tokens(token_count)

        if self.main_agent.pending_tool_calls:
            self._process_pending_tools()
            return

        status.update_status("Ready")

    # ── Tool processing ──

    def _process_pending_tools(self) -> None:
        """Route pending tool calls: immediate tools execute now, delegates spawn sub-agents."""
        tool_calls = list(self.main_agent.pending_tool_calls)
        chat = self.query_one("#chat-panel", ChatPanel)
        status = self.query_one(StatusBar)

        immediate_calls = [tc for tc in tool_calls if tc.name in _IMMEDIATE_TOOLS]
        delegate_calls = [tc for tc in tool_calls if tc.name == "delegate_task"]

        # Execute immediate tools (file ops) right away
        wrote_file = False
        for tc in immediate_calls:
            result = self._execute_tool(tc)
            self.main_agent.add_tool_result(tc.id, result)
            chat.show_user_message(f"[tool] {tc.name}: {self._tool_summary(tc)}")
            if tc.name == "write_file":
                wrote_file = True

        if wrote_file:
            file_tree = self.query_one("#file-tree-panel", FileTreePanel)
            file_tree.refresh_tree()

        if delegate_calls:
            status.update_status(f"Delegating {len(delegate_calls)} task(s)...")
            self._dispatch_sub_agents(delegate_calls)
            # _continue_agent will be called when all sub-agents finish
        else:
            # Only immediate tools — continue agent right away
            self._continue_agent()

    def _execute_tool(self, tc: AccumulatedToolCall) -> str:
        """Execute a non-delegate tool and return the result string."""
        if tc.name == "write_file":
            return self._tool_write_file(tc.arguments)
        elif tc.name == "read_file":
            return self._tool_read_file(tc.arguments)
        return f"Unknown tool: {tc.name}"

    def _tool_write_file(self, args: dict) -> str:
        path_str = args.get("path", "")
        content = args.get("content", "")
        if not path_str:
            return "Error: path is required"
        try:
            p = Path(path_str).expanduser()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"Wrote {len(content)} chars to {p}"
        except Exception as e:
            return f"Error writing file: {e}"

    def _tool_read_file(self, args: dict) -> str:
        path_str = args.get("path", "")
        if not path_str:
            return "Error: path is required"
        try:
            p = Path(path_str).expanduser()
            text = p.read_text(encoding="utf-8")
            if len(text) > 10_000:
                return text[:10_000] + f"\n... (truncated, {len(text)} chars total)"
            return text
        except Exception as e:
            return f"Error reading file: {e}"

    @staticmethod
    def _tool_summary(tc: AccumulatedToolCall) -> str:
        if tc.name == "write_file":
            return tc.arguments.get("path", "?")
        elif tc.name == "read_file":
            return tc.arguments.get("path", "?")
        return str(tc.arguments)[:80]

    # ── Sub-agent delegation ──

    def _dispatch_sub_agents(self, tool_calls: list[AccumulatedToolCall]) -> None:
        """Spawn sub-agents for each delegate_task tool call."""
        container = self.query_one("#agent-container", AgentContainer)
        self._expected_tool_calls = list(tool_calls)
        self._pending_results.clear()

        for tc in tool_calls:
            task = tc.arguments.get("task", "")
            worker_name = tc.arguments.get("worker_name", "Worker")
            agent_id = f"sub-{uuid.uuid4().hex[:8]}"

            panel_id = container.claim_panel(agent_id, worker_name)
            if panel_id is None:
                self.main_agent.add_tool_result(
                    tc.id, "Error: No free worker panel. Max 3 concurrent agents."
                )
                self._pending_results[tc.id] = "Error: No free panel"
                self._check_all_completed()
                continue

            sub_agent = SubAgent(
                provider=self._provider,
                agent_id=agent_id,
                worker_name=worker_name,
                task=task,
            )
            self._run_sub_agent(sub_agent, tc.id)

    @work(exclusive=False, group="sub-agents")
    async def _run_sub_agent(self, agent: SubAgent, tool_call_id: str) -> None:
        """Run a sub-agent and stream output to its panel."""
        container = self.query_one("#agent-container", AgentContainer)
        panel = container.get_panel(agent.agent_id)
        full_response = ""

        try:
            async for chunk in agent.send(agent.task):
                if chunk.type == "text":
                    full_response += chunk.content
                    if panel:
                        panel.append_token(chunk.content)
                elif chunk.type == "error":
                    if panel:
                        panel.show_error(chunk.content)
                    full_response += f"\nERROR: {chunk.content}"

            if panel:
                panel.finish_response()
                panel.set_status("done", label=agent.worker_name)

        except Exception as exc:
            full_response = f"Error: {exc}"
            if panel:
                panel.show_error(str(exc))

        self.post_message(
            SubAgentCompleted(
                agent_id=agent.agent_id,
                tool_call_id=tool_call_id,
                result=full_response or "(no output)",
            )
        )

    def on_sub_agent_completed(self, event: SubAgentCompleted) -> None:
        """Handle sub-agent completion: inject result and check if all done."""
        self.main_agent.add_tool_result(event.tool_call_id, event.result)
        self._pending_results[event.tool_call_id] = event.result
        self._check_all_completed()

    def _check_all_completed(self) -> None:
        """If all expected delegate calls have results, continue the main agent."""
        expected_ids = {tc.id for tc in self._expected_tool_calls}
        if expected_ids and expected_ids <= set(self._pending_results.keys()):
            self._expected_tool_calls.clear()
            self._continue_agent()

    # ── Continue after tools ──

    @work(exclusive=True, group="main-agent")
    async def _continue_agent(self) -> None:
        """Resume MainAgent after tool results are in."""
        chat = self.query_one("#chat-panel", ChatPanel)
        status = self.query_one(StatusBar)

        status.update_status("Synthesizing...")
        token_count = 0

        async for chunk in self.main_agent.continue_after_tools():
            if chunk.type == "text":
                chat.append_token(chunk.content)
                token_count += len(chunk.content) // 4
            elif chunk.type == "error":
                chat.show_error(chunk.content)

        chat.finish_response()
        status.update_tokens(token_count)

        # Check if the LLM wants more tool calls (e.g. delegate → write_file)
        if self.main_agent.pending_tool_calls:
            self._process_pending_tools()
            return

        status.update_status("Ready")
        self._pending_results.clear()

    # ── Keybindings ──

    def action_focus_chat(self) -> None:
        self.query_one("#chat-input").focus()

    def action_focus_terminal(self) -> None:
        self.query_one("#terminal-input").focus()

    def action_focus_tree(self) -> None:
        self.query_one("#file-tree").focus()

    def action_help(self) -> None:
        log = self.query_one("#chat-log")
        log.write("[#ffff55]F1[/]=Help [#ffff55]F2[/]=Chat [#ffff55]F7[/]=Term [#ffff55]F8[/]=Tree [#ffff55]F10[/]=Quit")
