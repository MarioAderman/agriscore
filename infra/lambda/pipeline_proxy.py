"""Lambda pipeline proxy — bridges Step Functions → FastAPI internal endpoints.

Receives {step, application_id} from Step Functions, POSTs to the FastAPI
internal endpoint via ALB, and returns the JSON result.

Environment variables:
  FASTAPI_BASE_URL — ALB DNS (e.g. http://agriscore-alb-123.us-east-1.elb.amazonaws.com)
"""

import json
import os
import urllib.error
import urllib.request

FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "http://localhost:8000")


def handler(event, context):
    """Lambda entry point. Called by Step Functions for each pipeline step.

    event shape: {"step": "extract-docs", "application_id": "uuid-here"}
    """
    step = event["step"]
    application_id = event["application_id"]

    url = f"{FASTAPI_BASE_URL}/api/internal/{step}/{application_id}"

    print(f"Pipeline proxy: POST {url}")

    req = urllib.request.Request(
        url,
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = json.loads(resp.read().decode())
            print(f"Pipeline proxy: {step} → {body.get('status', 'unknown')}")

            if body.get("status") == "error":
                raise Exception(f"Step {step} failed: {body.get('detail', 'unknown error')}")

            return body

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        print(f"Pipeline proxy: HTTP {e.code} from {step}: {error_body}")
        raise Exception(f"Step {step} returned HTTP {e.code}: {error_body}")

    except urllib.error.URLError as e:
        print(f"Pipeline proxy: connection error for {step}: {e.reason}")
        raise Exception(f"Step {step} unreachable: {e.reason}")
