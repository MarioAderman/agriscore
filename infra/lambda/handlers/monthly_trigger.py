"""Lambda handler: Monthly trigger — fan out re-evaluation for all active farmers."""

import json
import logging
import os

import boto3
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Query all completed applications and start a Step Functions execution per farmer."""
    sfn_arn = os.environ.get("STEP_FUNCTIONS_ARN", "")
    database_url = os.environ.get("DATABASE_URL", "")

    if not sfn_arn:
        logger.error("STEP_FUNCTIONS_ARN not configured")
        return {"status": "error", "error": "STEP_FUNCTIONS_ARN not set"}

    conn = psycopg2.connect(database_url)
    sfn = boto3.client("stepfunctions")

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT a.id
            FROM applications a
            WHERE a.status = 'completed'
            ORDER BY a.id
        """)
        applications = cur.fetchall()
        cur.close()

        started = 0
        for (app_id,) in applications:
            try:
                sfn.start_execution(
                    stateMachineArn=sfn_arn,
                    input=json.dumps({"application_id": str(app_id)}),
                )
                started += 1
            except Exception as e:
                logger.warning("Failed to start execution for %s: %s", app_id, e)

        logger.info("Monthly trigger: started %d executions out of %d applications", started, len(applications))
        return {"status": "completed", "started": started, "total": len(applications)}

    finally:
        conn.close()
