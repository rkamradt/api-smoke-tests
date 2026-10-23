"""
Entry point for the smoke test CronJob.
Runs pytest, emits a structured JSON summary to stdout for Loki ingestion,
sends a Gmail alert on failures, then exits with pytest's return code.
"""
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone

from notify import send_failure_alert

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


REPORT_FILE = "/tmp/smoke-report.json"


def main():
    result = subprocess.run(
        [
            "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--json-report",
            f"--json-report-file={REPORT_FILE}",
        ]
    )

    try:
        with open(REPORT_FILE) as f:
            report = json.load(f)

        summary = report.get("summary", {})
        failures = [
            {
                "test": t["nodeid"],
                "message": (t.get("call") or {}).get("longrepr", "")[:500],
            }
            for t in report.get("tests", [])
            if t["outcome"] in ("failed", "error")
        ]

        counts = {
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "error": summary.get("error", 0),
            "skipped": summary.get("skipped", 0),
            "total": summary.get("total", 0),
            "duration_s": round(report.get("duration", 0), 2),
        }

        print(json.dumps({
            "event": "smoke_test_run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **counts,
            "failures": failures,
        }), flush=True)

        if failures:
            send_failure_alert(failures, counts)

    except Exception as e:
        print(json.dumps({
            "event": "smoke_test_run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": f"failed to parse report: {e}",
        }), flush=True)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
