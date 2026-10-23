"""Gmail SMTP failure alert for api-smoke-tests."""

from __future__ import annotations

import logging
import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

_GMAIL_SMTP = "smtp.gmail.com"
_GMAIL_PORT = 587


def _build_plain(failures: list[dict], now: datetime, counts: dict) -> str:
    lines = [
        f"api-smoke-tests failure — {now.strftime('%Y-%m-%d %H:%M UTC')}",
        "=" * 60,
        f"passed: {counts['passed']}  failed: {counts['failed']}  "
        f"error: {counts['error']}  skipped: {counts['skipped']}  "
        f"total: {counts['total']}  duration: {counts['duration_s']}s",
        "",
    ]
    for f in failures:
        lines.append(f"FAIL  {f['test']}")
        if f.get("message"):
            for line in f["message"].splitlines():
                lines.append(f"      {line}")
        lines.append("")
    lines.append("--")
    lines.append("api-smoke-tests · https://github.com/rkamradt/api-smoke-tests")
    return "\n".join(lines)


def _build_html(failures: list[dict], now: datetime, counts: dict) -> str:
    rows = []
    for f in failures:
        msg_html = ""
        if f.get("message"):
            escaped = f["message"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            msg_html = f'<pre style="margin:4px 0 0 0;font-size:11px;color:#555;white-space:pre-wrap">{escaped}</pre>'
        rows.append(
            f'<tr style="border-bottom:1px solid #eee">'
            f'<td style="padding:8px 4px;color:#c0392b;font-weight:bold;white-space:nowrap">FAIL</td>'
            f'<td style="padding:8px 4px;font-family:monospace">{f["test"]}{msg_html}</td>'
            f'</tr>'
        )
    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")
    summary = (
        f'passed: <strong>{counts["passed"]}</strong> &nbsp;'
        f'failed: <strong style="color:#c0392b">{counts["failed"]}</strong> &nbsp;'
        f'error: <strong>{counts["error"]}</strong> &nbsp;'
        f'skipped: {counts["skipped"]} &nbsp;'
        f'total: {counts["total"]} &nbsp;'
        f'duration: {counts["duration_s"]}s'
    )
    return f"""<!DOCTYPE html>
<html>
<body style="font-family:sans-serif;max-width:700px;margin:auto;padding:16px">
  <h2 style="border-bottom:2px solid #c0392b;color:#c0392b">api-smoke-tests · Failures</h2>
  <p style="color:#555">{timestamp}</p>
  <p style="font-size:13px">{summary}</p>
  <table style="width:100%;border-collapse:collapse">
    <tbody>{"".join(rows)}</tbody>
  </table>
  <p style="font-size:11px;color:#999;margin-top:24px">
    api-smoke-tests · <a href="https://github.com/rkamradt/api-smoke-tests">github.com/rkamradt/api-smoke-tests</a>
  </p>
</body>
</html>"""


def send_failure_alert(failures: list[dict], counts: dict) -> None:
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not gmail_user or not gmail_app_password:
        logger.info("GMAIL_USER / GMAIL_APP_PASSWORD not set — skipping failure alert.")
        return

    to_addr = os.environ.get("GMAIL_TO", "randykamradt@gmail.com")
    now = datetime.now(tz=timezone.utc)
    n = counts["failed"] + counts["error"]
    subject = f"api-smoke-tests: {n} failure{'s' if n != 1 else ''} — {now.strftime('%Y-%m-%d %H:%M UTC')}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = to_addr
    msg.attach(MIMEText(_build_plain(failures, now, counts), "plain"))
    msg.attach(MIMEText(_build_html(failures, now, counts), "html"))

    logger.info("Sending failure alert to %s", to_addr)
    with smtplib.SMTP(_GMAIL_SMTP, _GMAIL_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(gmail_user, gmail_app_password)
        smtp.sendmail(gmail_user, [to_addr], msg.as_string())
    logger.info("Alert sent.")
