from env_file import env_varz
import controllers.MicroPreper.databasePreper as databasePreper
import controllers.MicroPreper.seleniumPreper as seleniumPreper
import controllers.MicroPreper.TodoPreper as todoPreper
from models.ScrappedChannel import ScrappedChannel
from models.Vod import Vod
from typing import List
env_varz.init_argz()

import controllers.MicroPreper.twitchApi as twitchApi


######################################################
# BEGIN                                              #
######################################################
if __name__ == "__main__":
    twitchApi.initAccessToken()
    topChannels = todoPreper.getTopChannelsSully()  # Make http request to sullygnome. 3rd party website
    topChannels = todoPreper.addVipList(topChannels, False) # same ^ but with gera
    scrapped_channels: List[ScrappedChannel] = todoPreper.instantiateJsonToClassObj(topChannels) # relevant_data = /mocks/initScrapData.py
    scrapped_channels = scrapped_channels[:int(env_varz.PREP_NUM_CHANNELS)]
    twitchApi.getVods(scrapped_channels)
    #########
    # twitchApi.getApiThing()