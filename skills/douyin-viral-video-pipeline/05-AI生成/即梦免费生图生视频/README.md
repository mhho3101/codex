# Jimeng Geek Skill

**Your browser session IS your API key.**

Use 即梦AI (jimeng.jianying.com / dreamina.capcut.com) image and video generation from CLI — for free — with a standard membership account. No paid API. No 高级会员. Works with any AI agent.

## The Idea

即梦 provides generous free generation through its web UI, but charges for official API access. The trick: your browser session cookie IS the API key. Extract it, call the same endpoints the browser calls, and you have free CLI generation.

This is NOT hacking. You're using your own authenticated session. The server treats your CLI calls exactly like browser requests.

## Quick Start

```bash
# 1. Install jimeng-cli
npm install -g jimeng-cli

# 2. Extract your session cookie from Chrome (auto)
pip install websocket-client
python3 scripts/extract_session.py --login

# 3. Generate!
jimeng image generate --prompt "a cat painting in watercolor style"
jimeng video generate --prompt "ocean waves at sunset" --wait
```

## Manual Cookie Extraction

If the script doesn't work:

1. Open Chrome → jimeng.jianying.com → login
2. DevTools (F12) → Application → Cookies → jimeng.jianying.com
3. Copy the `sessionid` cookie value
4. Run: `jimeng login --sessionid <value> --region cn`

## Features

- **Free image generation** — 4 candidates per call
- **Free video generation** — supports seedance, veo3, sora2 (region-dependent)
- **Multi-region** — cn, us, hk, jp, sg
- **Agent-friendly** — CLI + MCP server included
- **Batch ready** — see examples/batch_generate.sh

## Agent Integration

jimeng-cli works as a drop-in tool for any AI agent:

```python
# Python agent
import subprocess
subprocess.run(["jimeng", "image", "generate", "--prompt", prompt, "--ratio", "3:4"])
```

```bash
# MCP server mode (for native agent tool access)
jimeng-mcp
```

## The General Pattern

This approach works for ANY AIGC web service:

1. Login in browser
2. Find auth cookie (DevTools → Application → Cookies)
3. Find API endpoint (DevTools → Network → trigger action → find XHR)
4. Replicate request with cookie
5. Your web UI becomes your free API

## Documentation

- [SKILL.md](./SKILL.md) — Full method guide with pitfalls and integration patterns
- [scripts/extract_session.py](./scripts/extract_session.py) — Auto cookie extraction
- [examples/batch_generate.sh](./examples/batch_generate.sh) — Batch generation example

## License

MIT
