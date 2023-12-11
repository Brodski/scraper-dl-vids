
from models.AudioResponse import AudioResponse
from models.VodS3Response import VodS3Response
from models.Metadata_Ytdl import Metadata_Ytdl
from models.ScrappedChannel import ScrappedChannel
from models.Vod import Vod
from typing import List
from datetime import datetime

from dotenv import load_dotenv

import os
import MySQLdb


# load_dotenv()
import env_file as env_varz

connection = MySQLdb.connect(
    host    = env_varz.DATABASE_HOST,
    user    = env_varz.DATABASE_USERNAME,
    passwd  = env_varz.DATABASE_PASSWORD,
    db      = env_varz.DATABASE,
    autocommit  = True,
    ssl_mode    = "VERIFY_IDENTITY",
    ssl         = { "ca": "C:/Users/BrodskiTheGreat/Documents/HeidiSQL/cacert-2023-08-22.pem" } # See https://planetscale.com/docs/concepts/secure-connections#ca-root-configuration to determine the path to your operating systems certificate file.
)



def updateDbTodo(scrapped_channels: List[ScrappedChannel]):
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Tables in the database:")
        for table in tables:
            print(table[0])

    for scrapped_channel in scrapped_channels:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Vods (Description, NumberOfVods, Logo, Name) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (scrapped_channel.displayname,
                                scrapped_channel.language,
                                scrapped_channel.links,
                                scrapped_channel.logo,
                                scrapped_channel.rownum,
                                scrapped_channel.twitchurl,
                                scrapped_channel.url)
                            )
            connection.commit()


    current_utc_time = datetime.utcnow()
    formatted_utc_time = current_utc_time.strftime("%Y-%m-%d_%H:%M:%S")
    print("Formatted UTC Time:", formatted_utc_time)

    for scrapped_channel in scrapped_channels:
        order = 0
        for link in scrapped_channel.links:
            order = order + 1
            with connection.cursor() as cursor:
                sql = "INSERT INTO TODO (DateScrapped, Link, Order, FK_Channel, FK_VOD,) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (formatted_utc_time,
                                    link,
                                    order)
                                )
                connection.commit()




# CREATE TABLE Channels (
#     ID INT NOT NULL AUTO_INCREMENT,
#     Description VARCHAR(255),
#     NumberOfVods INT,
#     Logo VARCHAR(255),
#     Name VARCHAR(255),
#     PRIMARY KEY (ID)
# );

# CREATE TABLE Vods (
#     ID INT NOT NULL AUTO_INCREMENT,
#     URL VARCHAR(255),
#     ChannelID INT,
#     PRIMARY KEY (ID),
#     FOREIGN KEY (ChannelID) REFERENCES Channels(ID)
# );


# CREATE TABLE Todo (
#     ID INT NOT NULL AUTO_INCREMENT,
#     Status ENUM('todo', 'in progress', 'completed'),
#     VodID INT,
#     ChannelID INT,
#     PRIMARY KEY (ID),
#     FOREIGN KEY (VodID) REFERENCES Vods(ID),
#     FOREIGN KEY (ChannelID) REFERENCES Channels(ID)
# );
