"""Pipeline orchestrator — triggers Step Functions or runs locally."""

import asyncio
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def run_pipeline_local(application_id: str, base_url: str = "http://localhost:8000"):
    """Run all 5 pipeline steps locally via HTTP calls to the internal endpoints.

    Used for local development and as a fallback if Step Functions is not configured.
    """
    async with httpx.AsyncClient(timeout=120) as client:
        # Step 1: Extract docs
        logger.info("Pipeline: Step 1 — Extract docs")
        r = await client.post(f"{base_url}/api/internal/extract-docs/{application_id}")
        step1 = r.json()
        if step1.get("status") == "error":
            logger.error("Step 1 failed: %s", step1)
            return step1

        # Steps 2, 3a, 3b in parallel
        logger.info("Pipeline: Steps 2, 3a, 3b — Parallel fetch")
        results = await asyncio.gather(
            client.post(f"{base_url}/api/internal/fetch-satellite/{application_id}"),
            client.post(f"{base_url}/api/internal/fetch-climate/{application_id}"),
            client.post(f"{base_url}/api/internal/fetch-socioeconomic/{application_id}"),
            return_exceptions=True,
        )

        for i, r in enumerate(results):
            if isinstance(r, Exception):
                logger.error("Parallel step %d failed: %s", i + 2, r)
            else:
                try:
                    data = r.json()
                    logger.info("Parallel step result: %s — %s", data.get("step"), data.get("status"))
                except Exception:
                    logger.error("Parallel step %d returned non-JSON (status %s)", i + 2, r.status_code)

        # Step 4: Calculate score
        logger.info("Pipeline: Step 4 — Calculate score")
        r = await client.post(f"{base_url}/api/internal/calculate-score/{application_id}")
        step4 = r.json()
        if step4.get("status") == "error":
            logger.error("Step 4 failed: %s", step4)
            return step4

        # Step 5: Generate expediente
        logger.info("Pipeline: Step 5 — Generate expediente")
        r = await client.post(f"{base_url}/api/internal/generate-expediente/{application_id}")
        step5 = r.json()

        logger.info("Pipeline completed for %s: score=%.0f", application_id, step4.get("total_score", 0))
        return step5


async def trigger_step_functions(application_id: str):
    """Trigger AWS Step Functions execution.

    Falls back to local pipeline if Step Functions ARN is not configured.
    """
    if not settings.step_functions_arn:
        logger.info("Step Functions not configured — running pipeline locally")
        return await run_pipeline_local(application_id)

    # TODO: Implement Step Functions StartExecution via boto3
    import boto3
    import json

    sfn = boto3.client("stepfunctions", region_name=settings.aws_default_region)
    response = sfn.start_execution(
        stateMachineArn=settings.step_functions_arn,
        input=json.dumps({"application_id": str(application_id)}),
    )
    logger.info("Step Functions execution started: %s", response["executionArn"])
    return {"execution_arn": response["executionArn"]}
