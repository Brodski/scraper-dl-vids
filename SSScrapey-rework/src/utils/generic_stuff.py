from env_file import env_varz
from models.Vod import Vod
from typing import Dict, List
from utils.logging_config import LoggerConfig
import logging

def logger():
    pass
logger: logging.Logger = LoggerConfig("micro").get_logger()



def getFromFancyMap(d: dict[int, list]):
    # https://chatgpt.com/c/69278b8e-856c-8332-9475-66ce608d2298
    # data: Dict[int, List[Vod]] = {
    #     1: [a1,a2,a3],
    #     2: [b1,b2,b3,b4,b5,b6],
    #     3: [c1,c2],
    # }
    # outputs -> 1 column, 2nd column, 3rd, ....
    # outputs -> a1,b1,c1, a2,b2,c2, a3,b3, b4, b5, b6   
    keys = d.keys()
    max_len = max(len(d[k]) for k in keys)
    for x in range(max_len): # x = column
        for y in keys: # y = row
            row = d[y]
            if x < len(row):
                yield row[x] 

def convertToFancyMap(vod_list: List[Vod]) -> Dict[int, List[Vod]]:
    sub_list = []
    magical_ordered_map = {}
    previous = vod_list[0].channels_name_id # initialize
    idx_rank = 0
    for i, vod in enumerate(vod_list):
        current = vod.channels_name_id
        if previous != current:
            magical_ordered_map[idx_rank] = sub_list
            previous = current
            sub_list = []
            idx_rank += 1
        sub_list.append(vod)
    
    # Add the last group
    magical_ordered_map[idx_rank + 1] = sub_list

    mega_count = 0
    for key, v_list in magical_ordered_map.items():
        logger.debug(f"----------- {str(key)} -----------")
        for i, v in enumerate(v_list):
            v: Vod = v
            # logger.debug(i, " - ", v.channels_name_id, v.id, v.stream_date)
            logger.debug(f"{i} - {v.channels_name_id} {v.id} {v.stream_date}")
            mega_count += 1
    logger.debug("Total = " + str(mega_count))
    return magical_ordered_map