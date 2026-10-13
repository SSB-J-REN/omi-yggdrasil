import json, sys, time, urllib.request

OLLAMA = "http://localhost:11434/api/chat"
MODELS = sys.argv[1:]
if not MODELS:
    raise SystemExit("usage: python3 hermes_toolcall_test.py <model> [model ...]")

TOOLS = [
    {"type": "function", "function": {"name": "route_domain", "description": "Classify a request into one Hermes domain.",
     "parameters": {"type": "object", "properties": {"domain": {"type": "string", "enum": ["work", "homestead", "lab", "general"]}}, "required": ["domain"]}}},
    {"type": "function", "function": {"name": "search_wiki", "description": "Search the Obsidian wiki for stored notes and documents.",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "create_task", "description": "Create a task with a title and optional due date in YYYY-MM-DD.",
     "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "due": {"type": "string"}}, "required": ["title"]}}},
]
REQUIRED = {t["function"]["name"]: t["function"]["parameters"]["required"] for t in TOOLS}

SYSTEM = ("You are Hermes. For every user message call exactly one tool. "
          "Use route_domain when asked to route or classify something. "
          "Use search_wiki when asked what notes, the wiki, or past writing say. "
          "Use create_task when asked to add, track, or be reminded of something.")

CASES = [
    ("Route this: switchgear lineup delivery slipped two weeks", "route_domain", {"domain": "work"}),
    ("Route this: duck pond pump keeps losing prime", "route_domain", {"domain": "homestead"}),
    ("Route this: Ollama is offloading layers to CPU", "route_domain", {"domain": "lab"}),
    ("Route this: recommend a good book on Norse mythology", "route_domain", {"domain": "general"}),
    ("Route this: ER panel schedule needs updating after the RFI", "route_domain", {"domain": "work"}),
    ("Route this: chicken coop heat lamp breaker keeps tripping", "route_domain", {"domain": "homestead"}),
    ("What do my notes say about the generator ATS wiring?", "search_wiki", {}),
    ("Check the wiki for the Tailscale ACL setup", "search_wiki", {}),
    ("Find what I wrote about Meshtastic relay node placement", "search_wiki", {}),
    ("Add a task: chase the lighting package submittal by 2026-10-16", "create_task", {"due": "2026-10-16"}),
    ("Remind me to order more PLA filament", "create_task", {}),
    ("Track this: walk the endoscopy rough-in with the inspector on 2026-10-20", "create_task", {"due": "2026-10-20"}),
]

def chat(model, prompt):
    body = json.dumps({"model": model, "stream": False, "tools": TOOLS,
                       "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())

def grade(resp, tool, expect):
    calls = resp["message"].get("tool_calls") or []
    if len(calls) != 1:
        return f"expected 1 tool call, got {len(calls)}: {resp['message'].get('content', '')[:80]!r}"
    fn = calls[0]["function"]
    args = fn.get("arguments") or {}
    if fn["name"] != tool:
        return f"called {fn['name']} instead of {tool}"
    missing = [k for k in REQUIRED[tool] if not args.get(k)]
    if missing:
        return f"missing args {missing}: {args}"
    wrong = {k: args.get(k) for k, v in expect.items() if args.get(k) != v}
    if wrong:
        return f"wrong values {wrong}, expected {expect}"
    return None

for model in MODELS:
    chat(model, "Route this: warm-up")
    passed, secs, toks, tok_time, fails = 0, 0.0, 0, 0, []
    for prompt, tool, expect in CASES:
        t0 = time.time()
        resp = chat(model, prompt)
        secs += time.time() - t0
        toks += resp.get("eval_count", 0)
        tok_time += resp.get("eval_duration", 0)
        err = grade(resp, tool, expect)
        if err:
            fails.append(f"  FAIL  {prompt}\n        {err}")
        else:
            passed += 1
    tps = toks / (tok_time / 1e9) if tok_time else 0
    print(f"\n=== {model} ===")
    print(f"passed {passed}/{len(CASES)} | avg {secs / len(CASES):.1f}s per call | {tps:.1f} tok/s")
    print("\n".join(fails) if fails else "  no failures")
