import boto3
import os
import logging
import time

# Set up logging
logger = logging.getLogger("__name__")
logger.setLevel(logging.INFO)

# Initialize AWS client
sqs = boto3.client('sqs')

def lambda_handler(event, context):
    """
    Lambda function to re-drive messages from DLQs to their respective source queues.
    Accepts a list of DLQ URLs from the event or environment variables.
    """
    # Fetch DLQ URLs from the event or environment
    dlq_arns = os.getenv("DLQ_ARNS", "").split(",")
    if not dlq_arns:
        raise ValueError("No DLQ ARNS provided")
    logger.info(f"Re-driving queues: {dlq_arns} ", )

    results = []
    for dlq_arn in dlq_arns:
        try:
            logger.info(f"Processing DLQ: {dlq_arn}")

            # Start the re-drive task
            response = sqs.start_message_move_task(
                SourceArn=dlq_arn
            )
            task_id = response["TaskHandle"]
            logger.info(f"Re-drive task started for DLQ {dlq_arn}. TaskHandle: {task_id}")
            results.append({"dlq_arn": dlq_arn, "task_id": task_id})

        except Exception as e:
            logger.exception(f"Failed to process DLQ {dlq_arn}: {e}")
            results.append({"dlq_arn": dlq_arn, "error": str(e)})

    return {"results": results}