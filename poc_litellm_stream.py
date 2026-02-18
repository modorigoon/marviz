"""PoC: LiteLLM async streaming + tool_use (sub-agent 생성).

검증 목표:
1. litellm.acompletion(stream=True) → async for chunk
2. tool_use (function calling) → spawn_sub_agent 도구 호출 감지
3. 서브 에이전트가 독립 conversation history로 실행

실행: ANTHROPIC_API_KEY=sk-... python poc_litellm_stream.py
"""

import asyncio
import json
import os

import litellm

# ── 도구 정의 ──
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "spawn_sub_agent",
            "description": "Create a sub-agent to handle a specific task in parallel.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task for the sub-agent to perform",
                    },
                    "agent_name": {
                        "type": "string",
                        "description": "Name for the sub-agent",
                    },
                },
                "required": ["task", "agent_name"],
            },
        },
    }
]


async def test_basic_stream():
    """TEST 1: 기본 스트리밍."""
    print("=== TEST 1: Basic async streaming ===")
    response = await litellm.acompletion(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": "Say 'hello' in 3 languages. Be brief."}],
        stream=True,
        max_tokens=100,
    )

    tokens = []
    async for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            tokens.append(delta.content)
            print(delta.content, end="", flush=True)

    print()
    print(f"  Tokens received: {len(tokens)}")
    assert len(tokens) > 0, "Should have received tokens"
    print("  PASS")


async def test_tool_use():
    """TEST 2: tool_use로 sub-agent 생성 감지."""
    print("\n=== TEST 2: Tool use (spawn_sub_agent) ===")
    response = await litellm.acompletion(
        model="claude-sonnet-4-20250514",
        messages=[
            {
                "role": "user",
                "content": (
                    "I need you to analyze two things in parallel: "
                    "1) Check Python best practices "
                    "2) Review error handling patterns. "
                    "Use spawn_sub_agent for each task."
                ),
            }
        ],
        tools=TOOLS,
        stream=True,
        max_tokens=300,
    )

    text_parts = []
    tool_calls = []
    current_tool = None

    async for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            text_parts.append(delta.content)
            print(delta.content, end="", flush=True)
        if delta.tool_calls:
            for tc in delta.tool_calls:
                if tc.function and tc.function.name:
                    current_tool = {
                        "id": tc.id,
                        "name": tc.function.name,
                        "args": "",
                    }
                    tool_calls.append(current_tool)
                if tc.function and tc.function.arguments and current_tool:
                    current_tool["args"] += tc.function.arguments

    print()
    print(f"  Text parts: {len(text_parts)}")
    print(f"  Tool calls: {len(tool_calls)}")
    for tc in tool_calls:
        args = json.loads(tc["args"]) if tc["args"] else {}
        print(f"    - {tc['name']}({args})")
    assert len(tool_calls) > 0, "Should have tool calls"
    print("  PASS")


async def test_sub_agent_independent():
    """TEST 3: 서브 에이전트 독립 실행 (별도 conversation)."""
    print("\n=== TEST 3: Independent sub-agent streams ===")

    async def run_sub_agent(name: str, task: str):
        response = await litellm.acompletion(
            model="claude-sonnet-4-20250514",
            messages=[
                {
                    "role": "system",
                    "content": f"You are {name}. Complete the task concisely.",
                },
                {"role": "user", "content": task},
            ],
            stream=True,
            max_tokens=80,
        )
        tokens = []
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                tokens.append(delta.content)
        result = "".join(tokens)
        print(f"  {name}: {result[:60]}...")
        return len(tokens)

    # 3개 서브 에이전트 동시 실행
    results = await asyncio.gather(
        run_sub_agent("Worker-1", "List 3 Python best practices"),
        run_sub_agent("Worker-2", "List 3 error handling tips"),
        run_sub_agent("Worker-3", "List 3 testing strategies"),
    )

    print(f"  Token counts: {results}")
    assert all(r > 0 for r in results), "All agents should produce output"
    print("  PASS: 3 independent streams ran concurrently")


async def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set. Skipping LiteLLM tests.")
        print("Set it to run: export ANTHROPIC_API_KEY=sk-ant-...")
        return

    await test_basic_stream()
    await test_tool_use()
    await test_sub_agent_independent()

    print("\n" + "=" * 50)
    print("  ALL LITELLM FEASIBILITY TESTS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
