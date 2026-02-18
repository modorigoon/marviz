# Marviz

Terminal AI development environment with an MDIR/Norton Commander-style interface.

```
╔═══════════╦══════════════════╦═══════════╗
║           ║  Worker-1        ║ Files     ║
║  Main     ║──────────────────║───────────║
║  Agent    ║  Worker-2        ║ Editor    ║
║  (Chat)   ║──────────────────║           ║
║           ║  Worker-3        ║           ║
╠═══════════╩══════════════════╬═══════════╣
║  Status                      ║ Terminal  ║
╚══════════════════════════════╩═══════════╝
```

## Features

- Chat with an AI agent that can delegate tasks to up to 3 parallel workers
- Agents can read and write files directly
- Built-in file browser, code viewer, and terminal
- Supports any LLM provider via [LiteLLM](https://github.com/BerriAI/litellm) (Anthropic, OpenAI, Gemini, etc.)

## Setup

```bash
pip install -e ".[dev]"
```

Create `.env` in the project root:

```env
ANTHROPIC_API_KEY=sk-ant-...
```

Run:

```bash
marviz
```

## Tech Stack

Python 3.11+ / [Textual](https://github.com/Textualize/textual) / [LiteLLM](https://github.com/BerriAI/litellm) / asyncio

## License

MIT
