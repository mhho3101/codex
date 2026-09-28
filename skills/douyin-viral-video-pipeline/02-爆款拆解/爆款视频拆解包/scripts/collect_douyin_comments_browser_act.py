import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent

COMMENT_SECTION_START = "<!-- comments-insights:start -->"
COMMENT_SECTION_END = "<!-- comments-insights:end -->"

SCROLL_JS = r"""
(() => {
  const marker = document.querySelector(".comment-item-avatar");
  const allCandidates = Array.from(document.querySelectorAll("main, aside, section, div"))
    .filter((el) => {
      const style = window.getComputedStyle(el);
      const canScroll = el.scrollHeight - el.clientHeight > 120;
      const overflow = `${style.overflowY} ${style.overflow}`;
      return canScroll && /(auto|scroll|overlay)/i.test(overflow);
    });

  let candidates = [];
  if (marker) {
    candidates = allCandidates
      .filter((el) => el.contains(marker))
      .sort((a, b) => {
        const aRect = a.getBoundingClientRect();
        const bRect = b.getBoundingClientRect();
        return Math.abs(bRect.right - window.innerWidth) - Math.abs(aRect.right - window.innerWidth);
      })
      .slice(0, 2);
  }

  if (candidates.length === 0) {
    candidates = allCandidates
      .sort((a, b) => (b.scrollHeight - b.clientHeight) - (a.scrollHeight - a.clientHeight))
      .slice(0, 2);
  }

  for (const el of candidates) {
    el.scrollBy(0, Math.max(420, Math.floor(el.clientHeight * 0.65)));
  }

  return JSON.stringify({
    url: location.href,
    title: document.title,
    markerFound: Boolean(marker),
    scrolled: candidates.map((el) => ({
      tag: el.tagName,
      className: String(el.className || "").slice(0, 80),
      top: Math.round(el.scrollTop),
      height: el.clientHeight,
      scrollHeight: el.scrollHeight
    }))
  });
})()
"""

PAGE_META_JS = r"""
(() => JSON.stringify({ url: location.href, title: document.title }))()
"""

DOM_COMMENTS_JS = r"""
(() => {
  const seen = new Set();
  const out = [];
  const nodes = Array.from(document.querySelectorAll('[class*="comment"], [data-e2e*="comment"], div, span, p'));
  for (const el of nodes) {
    const rect = el.getBoundingClientRect();
    if (rect.width < 30 || rect.height < 8) continue;
    const raw = el.innerText || el.textContent || "";
    const text = raw.replace(/\s+/g, " ").trim();
    if (text.length < 2 || text.length > 220) continue;
    if (!/[\u4e00-\u9fa5A-Za-z0-9]/.test(text)) continue;
    if (/^(评论|点赞|分享|收藏|关注|登录|打开抖音|查看更多|展开|收起)$/.test(text)) continue;
    const key = text.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push({
      text,
      top: Math.round(rect.top),
      tag: el.tagName,
      className: String(el.className || "").slice(0, 80)
    });
    if (out.length >= 300) break;
  }
  return JSON.stringify(out);
})()
"""


def extract_url(text: str) -> str | None:
    match = re.search(r"https?://[^\s]+", text)
    if not match:
        return None
    return match.group(0).rstrip("，。,.!！?？")


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def run_browser_act(args: list[str], timeout: int = 60, check: bool = True) -> subprocess.CompletedProcess:
    if not shutil.which("browser-act"):
        raise RuntimeError("browser-act CLI not found. Install or fix PATH first.")
    cmd = ["browser-act", *args]
    try:
        proc = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        if check:
            raise
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        output = f"{output}\nTIMEOUT after {timeout}s: {' '.join(cmd)}"
        return subprocess.CompletedProcess(cmd, 124, output, None)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{proc.stdout}")
    return proc


def first_json_value(text: str) -> Any | None:
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char not in "[{\"":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, str):
            nested = first_json_value(value)
            return nested if nested is not None else value
        return value
    return None


def iter_json_values(text: str) -> list[Any]:
    values = []
    decoder = json.JSONDecoder()
    index = 0
    while index < len(text):
        char = text[index]
        if char not in "[{":
            index += 1
            continue
        try:
            value, end = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            index += 1
            continue
        values.append(value)
        index += max(end, 1)
    return values


def as_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    text = str(value).strip()
    if not text:
        return None
    text = text.replace(",", "")
    match = re.fullmatch(r"(\d+(?:\.\d+)?)([wW万kK]?)", text)
    if not match:
        return None
    number = float(match.group(1))
    suffix = match.group(2).lower()
    if suffix in ("w", "万"):
        number *= 10000
    elif suffix == "k":
        number *= 1000
    return int(number)


def first_key(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return data[key]
    return None


def clean_comment_text(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    text = re.sub(r"^[：:]+", "", text).strip()
    return text


def looks_like_comment_text(text: str) -> bool:
    if len(text) < 2 or len(text) > 220:
        return False
    if not re.search(r"[\u4e00-\u9fa5A-Za-z0-9]", text):
        return False
    blocked = (
        "打开抖音",
        "复制此链接",
        "登录",
        "分享",
        "收藏",
        "评论",
        "相关视频",
        "推荐",
        "广告",
    )
    if text in blocked:
        return False
    if text.startswith("http"):
        return False
    return True


def normalize_comment(data: dict[str, Any], source: str) -> dict[str, Any] | None:
    text = clean_comment_text(first_key(data, ("text", "content", "comment_text", "commentText", "reply_text")))
    if not looks_like_comment_text(text):
        return None

    has_comment_shape = any(
        key in data
        for key in (
            "cid",
            "comment_id",
            "commentId",
            "digg_count",
            "like_count",
            "reply_comment_total",
            "reply_count",
            "user",
        )
    )
    if not has_comment_shape:
        return None

    user = data.get("user") or data.get("author") or {}
    if not isinstance(user, dict):
        user = {}

    comment_id = first_key(data, ("cid", "comment_id", "commentId", "id"))
    like_count = as_int(first_key(data, ("digg_count", "like_count", "likeCount", "diggCount", "likes")))
    reply_count = as_int(
        first_key(data, ("reply_comment_total", "reply_count", "replyCommentTotal", "replyCount"))
    )

    return {
        "id": str(comment_id) if comment_id is not None else None,
        "text": text,
        "like_count": like_count,
        "reply_count": reply_count,
        "nickname": first_key(user, ("nickname", "name", "unique_id", "short_id")),
        "create_time": first_key(data, ("create_time", "createTime", "create_date")),
        "source": source,
    }


def collect_comments_from_obj(value: Any, source: str) -> list[dict[str, Any]]:
    found = []
    if isinstance(value, dict):
        item = normalize_comment(value, source)
        if item:
            found.append(item)
        for child in value.values():
            found.extend(collect_comments_from_obj(child, source))
    elif isinstance(value, list):
        for child in value:
            found.extend(collect_comments_from_obj(child, source))
    return found


def parse_request_ids(text: str) -> list[str]:
    ids = []
    keywords = ("comment", "reply", "aweme", "douyin")
    for line in text.splitlines():
        lowered = line.lower()
        if not any(keyword in lowered for keyword in keywords):
            continue
        match = re.search(r"\[(\d+)\]", line) or re.search(r"\bid[=:]\s*(\d+)", line, re.I)
        if match:
            request_id = match.group(1)
            if request_id not in ids:
                ids.append(request_id)
    return ids


def dedupe_comments(comments: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    seen = set()
    unique = []
    for comment in comments:
        key = comment.get("id") or comment.get("text")
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(comment)

    if any(comment.get("like_count") is not None for comment in unique):
        source_rank = {"network": 0, "state": 1, "dom": 2}
        unique.sort(
            key=lambda item: (
                item.get("like_count") is None,
                -(item.get("like_count") or 0),
                source_rank.get(str(item.get("source", "")).split(":", 1)[0], 9),
            )
        )
    for rank, comment in enumerate(unique[:limit], start=1):
        comment["rank"] = rank
    return unique[:limit]


def find_comment_click_index(state_text: str) -> str | None:
    metric_indices = re.findall(r"\[(\d+)\]<div class=[^\n]*\bAOWKbsTg\b", state_text)
    if len(metric_indices) >= 2:
        return metric_indices[1]

    for line in state_text.splitlines():
        if "评论" not in line:
            continue
        if not re.search(r"button|tab|a |<a|<button|role=", line, re.I):
            continue
        match = re.search(r"\[(\d+)\]", line)
        if match:
            return match.group(1)
    return None


def collect_dom_comments(session: str) -> list[dict[str, Any]]:
    proc = run_browser_act(["--session", session, "eval", DOM_COMMENTS_JS], timeout=60, check=False)
    value = first_json_value(proc.stdout)
    if not isinstance(value, list):
        return []
    comments = []
    for item in value:
        if not isinstance(item, dict):
            continue
        text = clean_comment_text(item.get("text"))
        if looks_like_comment_text(text):
            comments.append(
                {
                    "id": None,
                    "text": text,
                    "like_count": None,
                    "reply_count": None,
                    "nickname": None,
                    "create_time": None,
                    "source": "dom",
                }
            )
    return comments


STATE_COMMENT_SKIP = {
    "精选",
    "推荐",
    "关注",
    "朋友",
    "我的",
    "小游戏",
    "下载抖音精选",
    "搜索",
    "充钻石",
    "客户端",
    "壁纸",
    "通知",
    "私信",
    "投稿",
    "登录",
    "发送",
    "倍速",
    "智能",
    "清屏",
    "连播",
    "展开",
    "举报",
    "全部评论",
    "粉丝",
    "获赞",
    "推荐视频",
    "扫码登录",
    "如何扫码",
    "验证码登录",
    "密码登录",
    "获取验证码",
    "用户协议",
    "隐私政策",
    "打开",
    "扫一扫",
}


def looks_like_state_comment(line: str) -> bool:
    text = clean_comment_text(line)
    if not looks_like_comment_text(text):
        return False
    if text in STATE_COMMENT_SKIP:
        return False
    if text.startswith(("[", "|", "<", "url=", "title=", "class=", "发布时间：")):
        return False
    if re.fullmatch(r"[\d.]+[万wWkK]?", text):
        return False
    if re.fullmatch(r"\d{1,2}:\d{2}", text):
        return False
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", text):
        return False
    if text.startswith("#"):
        return False
    if "抖音APP" in text or "登录后" in text:
        return False
    footer_keywords = ("ICP备", "公网安备", "许可证", "举报", "bytedance.com", "douyin.com", "© 抖音")
    if any(keyword in text for keyword in footer_keywords):
        return False
    return True


def state_line_text(raw_line: str) -> str:
    line = re.sub(r"^\s+", "", raw_line)
    line = re.sub(r"^\[\d+\]\s*", "", line)
    return clean_comment_text(line)


def is_state_markup(text: str) -> bool:
    if not text:
        return True
    if text.startswith("|SCROLL|"):
        return True
    if text.startswith("<") or "<" in text:
        return True
    return False


def looks_like_comment_date(text: str) -> bool:
    return bool(
        re.fullmatch(r"(刚刚|昨天|前天|\d+分钟前|\d+小时前|\d+天前|\d+月前|\d+年前)(·\S+)?", text)
        or re.fullmatch(r"\d{4}-\d{2}-\d{2}(·\S+)?", text)
    )


def parse_real_comment_panel(state_text: str) -> list[dict[str, Any]]:
    comments: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    text_parts: list[str] = []
    in_comments = False
    pending_reply_count = False

    def finish_current() -> None:
        nonlocal current, text_parts, pending_reply_count
        if not current:
            return
        text = clean_comment_text(" ".join(text_parts))
        if not text and current.get("like_count") is not None:
            text = "[图片/表情评论]"
        if text:
            current["text"] = text
            comments.append(current)
        current = None
        text_parts = []
        pending_reply_count = False

    for raw_line in state_text.splitlines():
        raw_clean = raw_line.strip()
        text = state_line_text(raw_line)

        if text == "全部评论":
            in_comments = True
            continue
        if not in_comments and "comment-item-avatar" in raw_clean:
            in_comments = True
        if in_comments and (
            text == "推荐视频"
            or text.startswith("合集 ·")
            or re.fullmatch(r"\d{2}:\d{2}", text)
            or re.fullmatch(r"\d{1,2}:\d{2}:\d{2}", text)
        ):
            finish_current()
            in_comments = False
            continue
        if not in_comments:
            continue

        if "comment-item-avatar" in raw_clean:
            finish_current()
            current = {
                "id": None,
                "text": "",
                "like_count": None,
                "like_text": None,
                "reply_count": None,
                "nickname": None,
                "create_time": None,
                "source": "state_comment_panel",
            }
            continue

        if current is None or is_state_markup(text):
            continue

        if text in {"留下你的精彩评论吧", "分享", "回复"}:
            continue
        if text == "展开":
            pending_reply_count = True
            continue
        if pending_reply_count:
            value = as_int(text)
            if value is not None:
                current["reply_count"] = value
                continue
            if text == "条回复":
                pending_reply_count = False
                continue

        if looks_like_comment_date(text):
            current["create_time"] = text
            continue

        value = as_int(text)
        if current.get("create_time") and value is not None and current.get("like_count") is None:
            current["like_count"] = value
            current["like_text"] = text
            continue

        if text in {"...", "条回复"}:
            continue

        if current.get("nickname") is None:
            current["nickname"] = text
        else:
            text_parts.append(text)

    finish_current()
    return comments


def parse_video_overlay_comments(state_text: str) -> list[dict[str, Any]]:
    primary_lines = []
    secondary_lines = []
    in_comment_lane = False
    in_all_comments = False
    comments = []
    for raw_line in state_text.splitlines():
        text = state_line_text(raw_line)

        if text == "发送":
            in_comment_lane = True
            continue
        if in_comment_lane and (text.startswith("作者声明") or text == "展开"):
            in_comment_lane = False

        if text == "全部评论":
            in_all_comments = True
            continue
        if in_all_comments and text == "推荐视频":
            in_all_comments = False

        if in_comment_lane:
            primary_lines.append(text)
        elif in_all_comments:
            secondary_lines.append(text)

    source_lines = primary_lines or secondary_lines
    for text in source_lines:
        if looks_like_state_comment(text):
            comments.append(
                {
                    "id": None,
                    "text": text,
                    "like_count": None,
                    "reply_count": None,
                    "nickname": None,
                    "create_time": None,
                    "source": "state",
                }
            )
    return comments


def parse_state_comments(state_text: str) -> list[dict[str, Any]]:
    real_comments = parse_real_comment_panel(state_text)
    if real_comments:
        return real_comments
    return []


def collect_state_comments(session: str) -> list[dict[str, Any]]:
    proc = run_browser_act(["--session", session, "state"], timeout=60, check=False)
    return parse_state_comments(proc.stdout)


def collect_network_comments(session: str, max_requests: int) -> tuple[list[dict[str, Any]], list[str]]:
    requests_proc = run_browser_act(
        ["--session", session, "network", "requests", "--type", "xhr,fetch"],
        timeout=60,
        check=False,
    )
    request_ids = parse_request_ids(requests_proc.stdout)[:max_requests]
    comments = []
    inspected = []
    for request_id in request_ids:
        detail_proc = run_browser_act(
            ["--session", session, "network", "request", request_id],
            timeout=90,
            check=False,
        )
        inspected.append(request_id)
        for value in iter_json_values(detail_proc.stdout):
            comments.extend(collect_comments_from_obj(value, f"network:{request_id}"))
    return comments, inspected


def get_page_meta(session: str) -> dict[str, Any]:
    proc = run_browser_act(["--session", session, "eval", PAGE_META_JS], timeout=30, check=False)
    value = first_json_value(proc.stdout)
    return value if isinstance(value, dict) else {}


def open_and_scroll(args: argparse.Namespace, url: str, session: str) -> dict[str, Any]:
    open_args = ["--session", session, "browser", "open", args.browser_id, url]
    if args.headed:
        open_args.append("--headed")
    run_browser_act(open_args, timeout=120)
    run_browser_act(["--session", session, "wait", "stable", "--timeout", "30000"], timeout=45, check=False)

    state_proc = run_browser_act(["--session", session, "state"], timeout=45, check=False)
    initial_state_comments = parse_state_comments(state_proc.stdout)
    click_index = find_comment_click_index(state_proc.stdout)
    post_click_state_comments = []
    if click_index:
        run_browser_act(["--session", session, "click", click_index], timeout=30, check=False)
        run_browser_act(["--session", session, "wait", "stable", "--timeout", "15000"], timeout=25, check=False)
        post_click_state = run_browser_act(["--session", session, "state"], timeout=60, check=False)
        post_click_state_comments = parse_state_comments(post_click_state.stdout)

    scroll_snapshots = []
    scroll_state_comments = []
    for _ in range(args.scrolls):
        proc = run_browser_act(["--session", session, "eval", SCROLL_JS], timeout=30, check=False)
        value = first_json_value(proc.stdout)
        if isinstance(value, dict):
            scroll_snapshots.append(value)
        time.sleep(args.delay)
        scrolled_state = run_browser_act(["--session", session, "state"], timeout=60, check=False)
        scroll_state_comments.extend(parse_state_comments(scrolled_state.stdout))
    return {
        "clicked_comment_index": click_index,
        "initial_state_comments": initial_state_comments,
        "post_click_state_comments": post_click_state_comments,
        "scroll_state_comments": scroll_state_comments,
        "scroll_snapshots": scroll_snapshots,
    }


def resolve_output(args: argparse.Namespace) -> Path:
    if args.output:
        return args.output
    if args.package_dir:
        return args.package_dir / "_work" / "comments_raw.json"
    return SCRIPT_DIR / "_work" / "comments_raw.json"


def build_story_comment_section(result: dict[str, Any]) -> str:
    comments = result.get("comments", [])
    lines = [
        COMMENT_SECTION_START,
        "## 评论区洞察 / 底层心法",
        "",
        f"> 采集状态：共采集 {len(comments)} 条评论；网络接口 {result['quality']['network_comment_count']} 条，DOM {result['quality']['dom_comment_count']} 条，state 文本 {result['quality'].get('state_comment_count', 0)} 条。",
        "",
        "### 热评 TOP 拆解",
        "",
    ]
    for comment in comments[:10]:
        like = comment.get("like_count")
        like_text = "未知" if like is None else str(like)
        nickname = comment.get("nickname") or "未知用户"
        lines.append(f"- {comment['rank']}. {comment['text']}（点赞：{like_text}，用户：{nickname}）")

    if not comments:
        lines.append("- 暂未采集到可用评论。优先检查是否需要登录、评论区是否展开、页面是否触发风控。")

    lines += [
        "",
        "### 分析提示",
        "",
        "- 先看最高赞评论：它通常代表这条视频最强的共鸣点或吐槽角度。",
        "- 再看重复情绪：观众是在代入、骂人、接梗、争议，还是补充自己的经历。",
        "- 最后反推选题：把评论区高频情绪迁移成下一条内容的冲突、角色反应和金句。",
        "",
        COMMENT_SECTION_END,
    ]
    return "\n".join(lines) + "\n"


def update_story_analysis(path: Path, result: dict[str, Any]) -> None:
    section = build_story_comment_section(result)
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = "# 剧情分析\n\n"

    pattern = re.compile(
        re.escape(COMMENT_SECTION_START) + r".*?" + re.escape(COMMENT_SECTION_END) + r"\n?",
        re.S,
    )
    if pattern.search(text):
        text = pattern.sub(section, text)
    else:
        text = text.rstrip() + "\n\n" + section
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect Douyin comments with browser-act.")
    parser.add_argument("input", help="Douyin URL or copied share text.")
    parser.add_argument("--browser-id", default=os.environ.get("BROWSER_ACT_BROWSER_ID"), help="browser-act browser id.")
    parser.add_argument("--session", default=None, help="browser-act session name.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum comments to keep.")
    parser.add_argument("--scrolls", type=int, default=3, help="Number of comment scroll attempts.")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between scroll attempts.")
    parser.add_argument("--max-requests", type=int, default=20, help="Maximum network requests to inspect.")
    parser.add_argument("--skip-network", action="store_true", help="Do not inspect captured network responses.")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON path.")
    parser.add_argument("--package-dir", type=Path, default=None, help="Reference package directory.")
    parser.add_argument("--update-story", action="store_true", help="Append/update comment section in story_analysis.md.")
    parser.add_argument("--headed", action="store_true", help="Open visible browser window.")
    parser.add_argument("--keep-session", action="store_true", help="Keep browser-act session open after collection.")
    args = parser.parse_args()

    if not args.browser_id:
        print("Missing --browser-id. Run `browser-act browser list` and choose a Douyin-safe browser.", file=sys.stderr)
        return 2

    url = extract_url(args.input)
    if not url:
        print("No URL found in input.", file=sys.stderr)
        return 2

    session = args.session or f"douyin_comments_{now_stamp()}"
    output = resolve_output(args)
    output.parent.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc).isoformat()
    status = "ok"
    errors: list[str] = []
    scroll_info: dict[str, Any] = {}
    network_comments: list[dict[str, Any]] = []
    dom_comments: list[dict[str, Any]] = []
    state_comments: list[dict[str, Any]] = []
    inspected_requests: list[str] = []
    page_meta: dict[str, Any] = {}

    try:
        scroll_info = open_and_scroll(args, url, session)
        page_meta = get_page_meta(session)
        if not args.skip_network:
            network_comments, inspected_requests = collect_network_comments(session, args.max_requests)
        dom_comments = collect_dom_comments(session)
        state_comments = [
            *scroll_info.get("initial_state_comments", []),
            *scroll_info.get("post_click_state_comments", []),
            *scroll_info.get("scroll_state_comments", []),
            *collect_state_comments(session),
        ]
    except Exception as exc:
        status = "error"
        errors.append(str(exc))
    finally:
        if not args.keep_session:
            run_browser_act(["session", "close", session], timeout=30, check=False)

    primary_comments = [*network_comments, *state_comments]
    if not primary_comments:
        primary_comments = dom_comments
    comments = dedupe_comments(primary_comments, args.limit)
    if status == "ok" and not comments:
        status = "no_comments_found"

    result = {
        "status": status,
        "errors": errors,
        "input": args.input,
        "url": url,
        "final_url": page_meta.get("url"),
        "page_title": page_meta.get("title"),
        "collected_at": started_at,
        "browser_id": args.browser_id,
        "session": session,
        "quality": {
            "comment_count": len(comments),
            "network_comment_count": len(network_comments),
            "dom_comment_count": len(dom_comments),
            "state_comment_count": len(state_comments),
            "inspected_request_ids": inspected_requests,
            "clicked_comment_index": scroll_info.get("clicked_comment_index"),
            "scroll_rounds": len(scroll_info.get("scroll_snapshots", [])),
        },
        "debug": {
            "scroll_snapshots": scroll_info.get("scroll_snapshots", []),
            "post_click_state_comment_count": len(scroll_info.get("post_click_state_comments", [])),
            "scroll_state_comment_count": len(scroll_info.get("scroll_state_comments", [])),
        },
        "comments": comments,
    }

    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.update_story:
        story_path = (args.package_dir / "story_analysis.md") if args.package_dir else output.with_suffix(".md")
        update_story_analysis(story_path, result)

    print(f"Wrote {output}")
    print(f"Status: {result['status']}; comments: {len(comments)}")
    return 0 if status in ("ok", "no_comments_found") else 1


if __name__ == "__main__":
    raise SystemExit(main())
