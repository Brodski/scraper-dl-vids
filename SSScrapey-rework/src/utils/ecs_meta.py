import os
import requests

import logging
from utils.logging_config import LoggerConfig
from env_file import env_varz

def logger():
    pass

logger: logging.Logger = LoggerConfig("micro").get_logger()

def find_aws_logging_info():
    if env_varz.ENV == "local":
        return
    # Get metadata URI from environment variable
    metadata_uri = os.environ.get("ECS_CONTAINER_METADATA_URI_V4")
    if not metadata_uri:
        raise EnvironmentError("ECS_CONTAINER_METADATA_URI_V4 is not set")

    # Fetch task metadata
    response = requests.get(f"{metadata_uri}/task")
    response.raise_for_status()
    task_metadata = response.json
    logger.debug("response.json()")
    logger.debug(response.json())
    logger.debug("zzz")
    logger.debug("zzz")
    logger.debug("zzz")
    logger.debug("zzz")
    logger.debug("zzz")
    logger.debug("zzz")
    logger.debug("zzz")
    logger.debug("zzz")
    logger.debug("zzz")
    logger.debug("zzz")
    logger.debug("zzz")
    logger.debug("task_metadata")
    logger.debug(task_metadata)

    # Find your container (replace 'app' with your container name)
    container_name = "app"
    container_info = next(
        (c for c in task_metadata["Containers"] if c["Name"] == container_name), None
    )

    bski_contaier = task_metadata["Containers"][0] # the only container is my container

    log_options = bski_contaier["LogOptions"]
    awslogs_stream = log_options.get("awslogs-stream")
    awslogs_group  = log_options.get("awslogs-group")
    awslogs_region = log_options.get("awslogs-region")

    logger.info("Stream:", awslogs_stream)
    logger.info("Group:",  awslogs_group)
    logger.info("Region:", awslogs_region)

    if not awslogs_group:
        raise ValueError(f"Container {container_name} not found in metadata")

