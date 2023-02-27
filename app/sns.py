import boto3

import logging
import os

logger = logging.getLogger('django.server')

try:
    client = boto3.client(
        'sns',
        region_name='us-west-2',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    )
except Exception as e:
    logger.warning(f'Error when making SNS client: {e}')
    client = None

def send(topic_arn, subject, *msg):
    msg = '\n'.join(msg)
    if not client:
        logger.info(f"SNS credentials not set up, but if they were I'd send this message to {topic_arn}:\n{msg}")
        return
    client.publish(
        TopicArn=topic_arn,
        Message=msg,
        Subject=subject,
    )
