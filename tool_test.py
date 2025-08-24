#!/usr/bin/env python3
"""Minimal tool-calling test against llama.cpp's OpenAI-compatible server.
Usage:
  LLAMA_URL=http://localhost:8080/v1 LLAMA_MODEL=local python tool_test.py
Requires: requests (pip install requests)
"""
import os, json, requests
from datetime import datetime
try:
    from zoneinfo import ZoneInfo  # py>=3.9
except Exception:
    ZoneInfo = None

BASE = os.getenv("LLAMA_URL", "http://192.168.0.201:8080/v1")
MODEL = os.getenv("LLAMA_MODEL", "local")
API_KEY = os.getenv("LLAMA_API", "sk-no-key")  # llama.cpp ignores but header is required by some clients
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current local time for a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    }
]

SYSTEM = {
    "role": "system",
    "content": (
        "You are a helpful assistant. When a tool is useful, call it with valid JSON. "
        "Return final answers concisely."
    ),
}

USER = {"role": "user", "content": "What time is it in Tokyo right now?"}


def post_chat(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
        # llama.cpp often benefits from these, but they're optional:
        "temperature": 0,
    }
    r = requests.post(f"{BASE}/chat/completions", headers=HEADERS, data=json.dumps(payload), timeout=120)
    r.raise_for_status()
    return r.json()


def run_tool(name, args):
    if name == "get_time":
        city = (args.get("city") or "").strip()
        # naive city->tz mapping for demo
        tz = "Asia/Tokyo" if city.lower().startswith("tokyo") else "UTC"
        if ZoneInfo:
            now = datetime.now(ZoneInfo(tz)).isoformat()
        else:
            now = datetime.utcnow().isoformat() + "Z"
        return {"city": city, "tz": tz, "now": now}
    raise ValueError(f"Unknown tool: {name}")


def main():
    messages = [SYSTEM, USER]

    # First assistant response (may contain tool_calls)
    first = post_chat(messages)
    msg = first["choices"][0]["message"]
    messages.append(msg)

    tool_calls = msg.get("tool_calls") or []
    for call in tool_calls:
        if call.get("type") != "function":
            continue
        fn = call["function"]["name"]
        try:
            args = json.loads(call["function"].get("arguments") or "{}")
        except json.JSONDecodeError:
            args = {}
        result = run_tool(fn, args)
        messages.append({
            "role": "tool",
            "tool_call_id": call.get("id"),
            "content": json.dumps(result),
        })

    # Second assistant response should be the final answer using tool output
    final = post_chat(messages)
    print("\nASSISTANT:\n", final["choices"][0]["message"]["content"])


if __name__ == "__main__":
    main()
