---
name: jimeng-geek-skill
version: 1.0.0
author: Max & Hermes
description: >
  Use 即梦AI (Jimeng/Dreamina) image & video generation from CLI for free,
  with a standard (标准会员) account. No paid API needed.
  Your browser session IS your API key.
tags: [jimeng, dreamina, image-generation, video-generation, cli, agent, aigc, bytedance]
---

# Jimeng Geek Skill: Free CLI Image/Video Generation

**Your browser session IS your API key.**

Use 即梦AI (jimeng.jianying.com / dreamina.capcut.com) image and video generation
from CLI — for free — with a standard membership account. No paid API. No 高级会员.
Works with any AI agent (Hermes, Claude, Codex, etc.).

## The Method

即梦 provides a generous free tier through its web UI, but charges for official API access.
The trick is simple: extract your browser session cookie, then call the same HTTP endpoints
the browser uses. The server can't tell the difference.

```
1. You have a 即梦 account (even 标准会员 works)
2. Login in browser normally
3. Extract sessionid cookie
4. Call the web API directly from CLI
5. Free image/video generation, no API key needed
```

This pattern works because the web frontend and the "official API" hit the same backend.
The only difference is how you authenticate.

## Prerequisites

- A 即梦/Dreamina account (free or 标准会员)
- Node.js 18+ (for jimeng-cli)
- Chrome browser (for cookie extraction)
- Python 3 (for auto cookie extraction script, optional)

## Step 1: Install jimeng-cli

```bash
npm install -g jimeng-cli
```

jimeng-cli is a third-party CLI that wraps the jimeng web API.
It handles request construction, response parsing, and file downloading.

GitHub: https://github.com/Algovate/jimeng-cli

## Step 2: Get Your Session Cookie

You have 3 options, from most automated to manual:

### Option A: Auto-extract from Chrome (Recommended)

Use the provided script to extract the cookie from a running Chrome instance:

```bash
# Start Chrome with remote debugging enabled (if not already running)
# macOS:
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9333 &

# Linux:
google-chrome --remote-debugging-port=9333 &

# Then run the extraction script:
python3 scripts/extract_session.py
```

The script connects to Chrome via CDP, finds the sessionid cookie for
jimeng.jianying.com, and outputs it. Works for any logged-in session.

### Option B: Semi-auto via jimeng login

```bash
jimeng login --debug-port 9333
```

This tells jimeng-cli to connect to Chrome and extract the cookie automatically.
May require Python 3 and a helper script that sometimes is missing from the npm package.

### Option C: Manual (always works)

1. Open Chrome, go to jimeng.jianying.com
2. Make sure you are logged in
3. Open DevTools (F12 or Cmd+Option+I)
4. Go to Application tab → Cookies → jimeng.jianying.com
5. Find the cookie named `sessionid`
6. Copy its Value (this is your token)

Note: The sessionid cookie is httpOnly, so you CANNOT get it via
`document.cookie` in the console. You must use the Application tab.

## Step 3: Login to jimeng-cli

```bash
jimeng login --sessionid <your-sessionid-value> --region cn
```

Regions: `cn` (China mainland), `us` (USA), `hk` (Hong Kong),
`jp` (Japan), `sg` (Singapore).

Each region has different models and endpoints:
- cn: jimeng.jianying.com — most models, seedance video
- us/hk/jp/sg: dreamina.capcut.com — veo3, sora2 in some regions

## Step 4: Verify Token

```bash
jimeng token check
# [OK] abc123... (cn) live=true

jimeng token points
# Shows remaining credits (VIP credits are free for image generation)
```

## Step 5: Generate!

```bash
# Generate images (returns 4 candidates, picks first by default)
jimeng image generate --prompt "a watercolor painting of a cat reading a book"

# Generate with specific aspect ratio
jimeng image generate --prompt "mountain landscape at sunset" --ratio 3:4

# Generate with specific model
jimeng image generate --prompt "cyberpunk city" --model jimeng-3.0

# Generate video
jimeng video generate --prompt "ocean waves crashing on rocks" --wait

# List available models
jimeng models list --verbose

# Generate to specific output directory
jimeng image generate --prompt "..." --output-dir ./my-output/
```

Supported ratios: 1:1, 3:4, 4:3, 9:16, 16:9

## Agent Integration

### As a CLI tool in any agent

Just call `jimeng` from terminal in your agent's tool calls:

```python
import subprocess
result = subprocess.run([
    "jimeng", "image", "generate",
    "--prompt", prompt,
    "--ratio", "3:4",
    "--output-dir", output_dir
], capture_output=True, text=True)
```

### As MCP server for direct agent tool integration

jimeng-cli ships a built-in MCP server:

```bash
jimeng-mcp
```

Add it to your agent's MCP config to get native tool access
without shell calls.

### Pre-flight check pattern

Before any batch generation, always verify the token:

```bash
jimeng token check
# If not live, re-extract cookie and login again
```

## Batch Generation Pattern

For generating multiple images (e.g., comic panels, story illustrations):

```bash
# Pre-flight
jimeng token check || { echo "Token expired! Re-login needed."; exit 1; }

# Generate each image
for prompt in "panel 1: ..." "panel 2: ..." "panel 3: ..."; do
  jimeng image generate --prompt "$prompt" --ratio 3:4 --output-dir ./output/
done
```

Each call generates 4 images. Use vision model to pick the best one.

## Pitfalls & Gotchas

1. **Session expires on browser logout or cookie rotation.**
   If `jimeng token check` fails, re-extract the cookie.
   Typical session lifetime: a few days to weeks.

2. **Error 2038 is transient.**
   "图像生成失败，状态码: 30，错误码: 2038" — just retry with the same prompt.
   Usually succeeds on 2nd or 3rd attempt.

3. **4 images per call, need quality selection.**
   jimeng returns 4 candidates. Always use a vision model to pick the best one.
   Blindly taking image 1/4 wastes the multi-candidate advantage.

4. **httpOnly cookie — no JS extraction.**
   The sessionid cookie is httpOnly. You CANNOT use `document.cookie`.
   Must use DevTools Application tab or CDP (the extraction script).

5. **Region-specific models.**
   Some models (seedance, veo3, sora2) are only available in certain regions.
   Use `jimeng models list --region <region> --verbose` to check.

6. **VPN may interfere.**
   CN region endpoint (jimeng.jianying.com) may be blocked or slow outside China.
   Use `--region us` or `--region sg` for international access via dreamina.capcut.com.

7. **Credits may not deduct for image gen.**
   With VIP status, image generation often doesn't consume credits.
   But video generation may consume credits depending on model.

## The Generalized Pattern

This method is not specific to 即梦. The same approach works for any
AIGC web service that:

1. Has a free or freemium web UI
2. Uses cookie-based authentication
3. Makes API calls from the browser to a backend

The steps are always the same:
1. Login in browser
2. Find the auth cookie (DevTools → Application → Cookies)
3. Find the API endpoint (DevTools → Network tab, trigger an action, find the XHR)
4. Replicate the request with the cookie
5. Parse the response

This pattern turns any web UI into a free API.

## File Structure

```
jimeng-geek-skill/
├── SKILL.md                  # This file — the method + guide
├── README.md                 # GitHub landing page
├── scripts/
│   └── extract_session.py    # Auto cookie extraction from Chrome
├── examples/
│   └── batch_generate.sh     # Example batch generation script
└── LICENSE                   # MIT
```

## License

MIT — use freely, share widely.

## Disclaimer

This method uses your own browser session to access services you are already
authenticated to. It does not bypass authentication or access any unauthorized
resources. However, it may violate the Terms of Service of some platforms.
Use at your own risk.
