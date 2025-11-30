import os
import requests

import logging
from utils.logging_config import LoggerConfig

def logger():
    pass

logger: logging.Logger = LoggerConfig("micro").get_logger()

def find_aws_logging_info():
    # Get metadata URI from environment variable
    metadata_uri = os.environ.get("ECS_CONTAINER_METADATA_URI_V4")
    if not metadata_uri:
        raise EnvironmentError("ECS_CONTAINER_METADATA_URI_V4 is not set")

    # Fetch task metadata
    response = requests.get(f"{metadata_uri}/task")
    response.raise_for_status()
    task_metadata = response.json()

    # Find your container (replace 'app' with your container name)
    container_name = "app"
    container_info = next(
        (c for c in task_metadata["Containers"] if c["Name"] == container_name), None
    )

    if not container_info:
        raise ValueError(f"Container {container_name} not found in metadata")

    # Extract log info
    log_options = container_info.get("LogOptions", {})
    log_group = log_options.get("awslogs-group")
    log_stream = log_options.get("awslogs-stream")
    region = log_options.get("awslogs-region")

    logger.info("Region:", region)
    logger.info("Log Group:", log_group)
    logger.info("Log Stream:", log_stream)
