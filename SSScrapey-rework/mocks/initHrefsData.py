from models.ScrappedChannel import ScrappedChannel

hrefData = [
   {
      "displayname": "Nmplol",
      "language": "English",
      "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/e4d9bf96-311d-487a-b5eb-9f9a94e0f795-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
      "twitchurl": "https://www.twitch.tv/nmplol",
      "url": "nmplol",
      "links": [
         "/videos/40792901",
         "/videos/1470165627"
      ],
      "current_rank": -1,
      "todos":[
         
      ]
   },
   # {
   #    "displayname": "台北建東",
   #    "language": "Chinese",
   #    "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/14b5d29d-d934-485d-aa1d-12d44e05f77e-profile_image-70x70.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
   #    "twitchurl": "https://www.twitch.tv/jd_onlymusic",
   #    "url": "jd_onlymusic",
   #    "links": [
   #       "/videos/1964894986",
   #    ],
   #    "current_rank": -3,
   #    "todos":[         
   #    ]
   # },
   {
      "displayname":"LoLGeranimo",
      "language":"English",
      "logo":"https://static-cdn.jtvnw.net/jtv_user_pictures/4d5cbbf5-a535-4e50-a433-b9c04eef2679-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
      "twitchurl":"https://www.twitch.tv/lolgeranimo",
      "url":"lolgeranimo",
      "current_rank": -2,
      "links":[
         "/videos/5057810",
         "/videos/28138895"
      ]
   },
   # {
   #    "displayname":"LCK",
   #    "language":"English",
   #    "logo":"https://static-cdn.jtvnw.net/jtv_user_pictures/04b097ac-9a71-409e-b30e-570175b39caf-profile_image-150x150.png?imenable=1&impolicy=user-profile-picture&imwidth=100",
   #    "twitchurl":"https://www.twitch.tv/lck",
   #    "url":"lck",
   #    "links":[
   #       "/videos/576354726",
   #       "/videos/1108764940"
   #    ]
      # "current_rank": -4,
   # }
]

# def getHrefsData():
#     channels = []
#     for data in hrefData:
#         scrapped_channel = ScrappedChannel(displayname=data.get("displayname"),
#                                            language=data.get("language"),
#                                            logo=data.get("logo"),
#                                            links=data.get("links"),
#                                            twitchurl=data.get("twitchurl"),
#                                            name_id=data.get("url"),
#                                            current_rank=data.get("current_rank"))
#         channels.insert(0,scrapped_channel)
#     return channels
