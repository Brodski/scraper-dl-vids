import os
import traceback
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
    try:
        metadata_uri = os.environ.get("ECS_CONTAINER_METADATA_URI_V4")
        if not metadata_uri:
            raise EnvironmentError("ECS_CONTAINER_METADATA_URI_V4 is not set")

        response = requests.get(f"{metadata_uri}/task")
        response.raise_for_status()
        task_metadata = response.json()
        # logger.debug("task_metadata")
        # logger.debug(task_metadata)

        bski_contaier = task_metadata["Containers"][0] # the only container is my container

        log_options = bski_contaier["LogOptions"]
        awslogs_stream: str = log_options.get("awslogs-stream")
        awslogs_group:  str = log_options.get("awslogs-group")
        awslogs_region: str = log_options.get("awslogs-region")

        logger.info("Stream: " + awslogs_stream)
        logger.info("Group: " +  awslogs_group)
        logger.info("Region: " + awslogs_region)


        cli = get_aws_cli_view_logs()

        return cli
        return awslogs_stream, awslogs_group, awslogs_region
    except:
        stack = traceback.format_exc()
        logger.error("something broke with aws cli cloudwatch finder")
        logger.error(stack)

def find_aws_logging_info_transcriber():
    if env_varz.ENV == "local":
         return
    from controllers.MicroTranscriber.Cloudwatch import Cloudwatch
    cloudwatch: Cloudwatch = Cloudwatch()
    awslogs_group = cloudwatch.LOG_GROUP_NAME
    awslogs_stream = cloudwatch.LOG_STREAM_NAME
    awslogs_region = "us-east-1"
    cli = get_aws_cli_view_logs(awslogs_stream, awslogs_group, awslogs_region)
    return cli


def get_aws_cli_view_logs(awslogs_stream, awslogs_group, awslogs_region):
        out_ = f"C:\\Users\\BrodskiTheGreat\\Desktop\\desktop\\Code\\scraper-dl-vids\\logs\\{awslogs_stream}.txt".replace("/", ".").replace("\\", ".")
        cli = "\n"
        cli = cli + 'set PYTHONUTF8=1\n'
        cli = cli + 'aws logs get-log-events '
        cli = cli + f' --log-group-name "{awslogs_group}" '
        cli = cli + f' --log-stream-name "{awslogs_stream}" '
        cli = cli + f' --region {awslogs_region} '
        cli = cli + f' --output text > "{out_}" \n\n'

        logger.info(" ################################")
        logger.info(" ######                    ######")
        logger.info(" ###### AWS CLI - get logs ######")
        logger.info(" ######                    ######")
        logger.info(" ################################")
        logger.info(cli)

        return cli

