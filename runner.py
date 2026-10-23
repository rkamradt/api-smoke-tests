"""
Entry point for the smoke test CronJob.
Runs pytest, emits a structured JSON summary to stdout for Loki ingestion,
then exits with pytest's return code so the CronJob status reflects pass/fail.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone


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

        print(json.dumps({
            "event": "smoke_test_run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "error": summary.get("error", 0),
            "skipped": summary.get("skipped", 0),
            "total": summary.get("total", 0),
            "duration_s": round(report.get("duration", 0), 2),
            "failures": failures,
        }), flush=True)

    except Exception as e:
        print(json.dumps({
            "event": "smoke_test_run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": f"failed to parse report: {e}",
        }), flush=True)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
