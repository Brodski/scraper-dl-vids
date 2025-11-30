from typing import List
from env_file import env_varz
from models.Vod import Vod
from models.ScrappedChannel import ScrappedChannel
from utils.emailer import sendEmail
import logging
from utils.logging_config import LoggerConfig
from utils.ecs_meta import find_aws_logging_info

def logger():
    pass

logger: logging.Logger = LoggerConfig("micro").get_logger()


class MetadataP:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        # Example variables
        self.vods_updated = {}
        self.elapsed_time = None
        self.new_channels: List[ScrappedChannel] = []
        # self.new_vods: List[Vod] = None
        self.deleted_olds_num = None
        self.num_channels_updated_via_sully = None
        self.num_channels_updated_via_sully_actual = None

        self._initialized = True


    def format_and_email_msg(self):
        subject = f"Preper {env_varz.ENV} Report"
        elapsed_time_MIN = round(self.elapsed_time / 60, 2)
        msg_chan = ""
        for chan in self.new_channels:
            chan: ScrappedChannel = chan
            msg_chan = msg_chan + f"{chan.name_id}, "
        msg_vod = ""
        # for vod in self.new_vods:
        #     vod: Vod = vod
        #     msg_vod = msg_vod + f"{vod.channels_name_id} - {vod.id}\n"

        msg_vods_updated = ""
        count = 0
        for name_id, info in self.vods_updated.items():
            for key, value in info.items():
                # print(name_id, key, value)
                msg_vods_updated += f"    {name_id}, {key}, {value}\n"
                count = count + 1
        msg_vods_updated = msg_vods_updated + "Total vods existing + new = " + str(count)

        cli = find_aws_logging_info()
            
        lines = [
            "Metadata Summary",
            "----------------",
            f"Elapsed Time: {self.elapsed_time} = {elapsed_time_MIN} min",
            f"New Channels: {msg_chan}",
            # f"New VODs: \n{self.new_vods}",
            f"msg_vods_updated (prev_existing = not new): \n{msg_vods_updated}",
            f"Deleted Old Items count: {self.deleted_olds_num}",
            f"Expected PREP_NUM_CHANNELS: {env_varz.PREP_NUM_CHANNELS}",
            f"Expected PREP_NUM_VOD_PER_CHANNEL: {env_varz.PREP_NUM_VOD_PER_CHANNEL}",
            f"Expected num chans updated via Sully updated : {self.num_channels_updated_via_sully}",
            f"Actual chan's updated via Sully updated : {self.num_channels_updated_via_sully_actual}",
            f"cli = \n{cli}",
        ]

        body = "\n".join(lines)

        logger.info(subject)
        logger.info(body)

        sendEmail(subject, body)
        return body


    # Example methods
    def set(self, key, value):
        self.settings[key] = value
    def get(self, key):
        return self.settings.get(key)
    def info(self):
        return f"env={self.environment}, version={self.version}"