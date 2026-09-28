#!/usr/bin/env python3
"""
Extract sessionid cookie from a running Chrome instance via Chrome DevTools Protocol.

Usage:
    python3 extract_session.py [--debug-port PORT] [--domain DOMAIN] [--login]

Options:
    --debug-port PORT   Chrome remote debugging port (default: 9333)
    --domain DOMAIN     Cookie domain to search (default: jimeng.jianying.com)
    --login             Auto-run 'jimeng login --sessionid <token>' after extraction

Prerequisites:
    - Chrome must be running with --remote-debugging-port=PORT
    - You must be logged in to jimeng.jianying.com in Chrome

To start Chrome with debugging enabled:
    macOS:   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9333 &
    Linux:   google-chrome --remote-debugging-port=9333 &
    Windows: chrome.exe --remote-debugging-port=9333
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
import urllib.error


def get_ws_url(debug_port: int) -> str:
    """Get WebSocket debugger URL from Chrome."""
    url = f"http://127.0.0.1:{debug_port}/json/version"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
            return data.get("webSocketDebuggerUrl")
    except urllib.error.URLError as e:
        print(f"[ERROR] Cannot connect to Chrome on port {debug_port}", file=sys.stderr)
        print(f"        Make sure Chrome is running with --remote-debugging-port={debug_port}", file=sys.stderr)
        print(f"        Detail: {e}", file=sys.stderr)
        sys.exit(1)


def get_cookies_via_cdp(debug_port: int, domain: str) -> list:
    """Get cookies from Chrome via CDP using raw WebSocket.

    Uses only stdlib to avoid dependencies.
    Falls back to /json/list if websocket is not available.
    """
    # Try the simple HTTP endpoint first — some Chrome versions expose cookies
    # via the Network domain through a page target.
    # We'll use a trick: find a page target, then use CDP over HTTP.

    # Step 1: List available targets
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{debug_port}/json/list", timeout=5) as resp:
            targets = json.loads(resp.read())
    except Exception as e:
        print(f"[ERROR] Cannot list Chrome targets: {e}", file=sys.stderr)
        sys.exit(1)

    # Find a suitable page target
    page_target = None
    for t in targets:
        if t.get("type") == "page":
            page_target = t
            break

    if not page_target:
        print("[ERROR] No page targets found in Chrome. Open a tab first.", file=sys.stderr)
        sys.exit(1)

    # Step 2: Use CDP via WebSocket to get cookies
    # Since we want zero dependencies, we'll try the websocket approach
    # but fall back to a hint if the module is unavailable.
    try:
        import websocket  # noqa: try websocket-client
    except ImportError:
        # Fall back: try to install websocket-client, or use alternative method
        print("[INFO] websocket-client not installed, trying to use built-in approach...", file=sys.stderr)
        return _get_cookies_simple(debug_port, domain)

    ws_url = page_target.get("webSocketDebuggerUrl")
    if not ws_url:
        print("[ERROR] No WebSocket URL for target", file=sys.stderr)
        sys.exit(1)

    return _get_cookies_ws(ws_url, domain)


def _get_cookies_ws(ws_url: str, domain: str) -> list:
    """Get cookies via WebSocket CDP connection."""
    try:
        import websocket
    except ImportError:
        print("[ERROR] websocket-client required. Install: pip install websocket-client", file=sys.stderr)
        sys.exit(1)

    ws = websocket.create_connection(ws_url, timeout=10)

    # Send CDP command to get all cookies
    cmd = {"id": 1, "method": "Network.getAllCookies"}
    ws.send(json.dumps(cmd))
    result = json.loads(ws.recv())
    ws.close()

    cookies = result.get("result", {}).get("cookies", [])
    return [c for c in cookies if domain in c.get("domain", "")]


def _get_cookies_simple(debug_port: int, domain: str) -> list:
    """Fallback: extract cookies by navigating a new tab to the target domain.

    This approach creates a new tab, navigates to the domain,
    then reads cookies via CDP. Less reliable but no websocket dependency.
    """
    # Create a new tab
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{debug_port}/json/new?https://{domain}",
            timeout=10
        ) as resp:
            tab = json.loads(resp.read())
    except Exception as e:
        print(f"[ERROR] Cannot create new tab: {e}", file=sys.stderr)
        print("[HINT] Install websocket-client for reliable extraction:", file=sys.stderr)
        print("       pip install websocket-client", file=sys.stderr)
        sys.exit(1)

    ws_url = tab.get("webSocketDebuggerUrl")
    if not ws_url:
        print("[ERROR] No WebSocket URL. Try: pip install websocket-client", file=sys.stderr)
        sys.exit(1)

    return _get_cookies_ws(ws_url, domain)


def extract_sessionid(debug_port: int, domain: str) -> str | None:
    """Extract the sessionid cookie for the given domain."""
    print(f"[*] Connecting to Chrome on port {debug_port}...")
    print(f"[*] Looking for sessionid on {domain}...")

    cookies = get_cookies_via_cdp(debug_port, domain)

    if not cookies:
        print(f"[WARN] No cookies found for {domain}", file=sys.stderr)
        print(f"        Make sure you are logged in to {domain} in Chrome", file=sys.stderr)
        return None

    # Find sessionid cookie
    for c in cookies:
        if c.get("name") == "sessionid":
            return c.get("value")

    # List what we found for debugging
    print(f"[WARN] No 'sessionid' cookie found for {domain}", file=sys.stderr)
    print(f"       Found cookies: {[c['name'] for c in cookies]}", file=sys.stderr)
    return None


def run_jimeng_login(sessionid: str, region: str = "cn") -> bool:
    """Run jimeng login with the extracted sessionid."""
    cmd = ["jimeng", "login", "--sessionid", sessionid, "--region", region]
    print(f"\n[RUN] {' '.join(cmd[:3])} *** --region {region}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except FileNotFoundError:
        print("[ERROR] 'jimeng' CLI not found. Install: npm install -g jimeng-cli", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("[ERROR] jimeng login timed out", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Extract sessionid cookie from Chrome for jimeng CLI login"
    )
    parser.add_argument(
        "--debug-port", type=int, default=9333,
        help="Chrome remote debugging port (default: 9333)"
    )
    parser.add_argument(
        "--domain", default="jimeng.jianying.com",
        help="Cookie domain to search (default: jimeng.jianying.com)"
    )
    parser.add_argument(
        "--region", default="cn",
        choices=["cn", "us", "hk", "jp", "sg"],
        help="Region for jimeng login (default: cn)"
    )
    parser.add_argument(
        "--login", action="store_true",
        help="Auto-run 'jimeng login --sessionid <token>' after extraction"
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Also run 'jimeng token check' after login"
    )
    args = parser.parse_args()

    sessionid = extract_sessionid(args.debug_port, args.domain)

    if not sessionid:
        print("\n[FAIL] Could not extract sessionid.")
        print("\nManual extraction steps:")
        print(f"  1. Open Chrome, go to {args.domain}")
        print("  2. Make sure you are logged in")
        print("  3. DevTools (F12) → Application → Cookies")
        print(f"  4. Copy the 'sessionid' cookie value")
        print(f"  5. Run: jimeng login --sessionid <value> --region {args.region}")
        sys.exit(1)

    # Mask for display
    masked = sessionid[:8] + "..." + sessionid[-4:] if len(sessionid) > 12 else sessionid
    print(f"\n[OK] Found sessionid: {masked}")

    if args.login:
        success = run_jimeng_login(sessionid, args.region)
        if not success:
            sys.exit(1)

        if args.check:
            print("\n[*] Verifying token...")
            subprocess.run(["jimeng", "token", "check"], timeout=15)
    else:
        print(f"\nTo login, run:")
        print(f"  jimeng login --sessionid {sessionid} --region {args.region}")
        print(f"\nOr re-run with --login flag to do it automatically.")


if __name__ == "__main__":
    main()
