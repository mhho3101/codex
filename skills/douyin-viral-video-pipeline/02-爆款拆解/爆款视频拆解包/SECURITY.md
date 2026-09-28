# Security And Privacy

This skill runs local video tooling and may use a logged-in browser session for
Douyin comment collection or Douyin download fallback.

## Sensitive Data

Do not commit:

- exported cookies
- browser profiles
- screenshots containing private account data
- generated `_work/` folders
- downloaded videos you do not have rights to redistribute
- HuggingFace, ModelScope, platform, or API credentials
- machine-specific `references/local-setup.private.md`

## BrowserAct Usage

The default integrated comment run uses `--skip-network`, which avoids reading
captured network responses. The standalone comment collector can inspect network
responses when `--skip-network` is omitted; use that only when you understand
what data may be exposed in your local browser session.

## Reporting

If you find a security issue, open a private report or contact the maintainer
instead of posting sensitive details in a public issue.
