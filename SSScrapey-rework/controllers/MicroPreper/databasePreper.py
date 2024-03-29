from datetime import datetime
from dotenv import load_dotenv
from models.ScrappedChannel import ScrappedChannel
from typing import List
import env_file as env_varz
import MySQLdb
import os

def getConnection():
    print('got connection')
    connection = MySQLdb.connect(
        host    = env_varz.DATABASE_HOST,
        user    = env_varz.DATABASE_USERNAME,
        passwd  = env_varz.DATABASE_PASSWORD,
        db      = env_varz.DATABASE,
        autocommit  = False,
        ssl_mode    = "VERIFY_IDENTITY",
        ssl         = { "ca": env_varz.SSL_FILE } # See https://planetscale.com/docs/concepts/secure-connections#ca-root-configuration to determine the path to your operating systems certificate file.
    )
    return connection


def addRankingsForTodayDb(scrapped_channels: List[ScrappedChannel]):
    connection = getConnection()
    with connection.cursor() as cursor:
        values = [(chan.name_id, int(chan.current_rank)) for chan in scrapped_channels]
        sql = "INSERT INTO Rankings (TodoDate, ChannelNameId, Ranking) VALUES (NOW(), %s, %s)"
        print("Adding new Ranks:", str(values))
        print("Adding new sql:", str(sql))
        try:
            with connection.cursor() as cursor:
                cursor.executemany(sql, values)  # Batch insert
            connection.commit()
        except Exception as e:
            print(f"Error occurred (addRankingsForTodayDb): {e}")
            connection.rollback()
    connection.close()

def addNewChannelToDb(scrapped_channels: List[ScrappedChannel]):
    connection = getConnection()
    with connection.cursor() as cursor:
        # Make SQL Query
        name_ids = [chn.name_id for chn in scrapped_channels]
        formatted_ids = ', '.join([f"'{str(name)}'" for name in name_ids])
        query = f"SELECT NameId FROM Channels WHERE NameId IN ({formatted_ids})"

        cursor.execute(query)

        # Get results
        existing_name_ids = [row[0] for row in cursor.fetchall()]
        non_existing_name_ids = set(name_ids) - set(existing_name_ids)
        new_channels = [chan for chan in scrapped_channels if chan.name_id not in existing_name_ids]

        print("Existing IDs:", existing_name_ids)
        print("New IDs: " + str(new_channels))

        # Add new channels to database
        if new_channels:
            sql = "INSERT INTO Channels (DisplayName, Language, Logo, CurrentRank, TwitchUrl, NameId) VALUES (%s, %s, %s, %s, %s, %s)"
            values = [(chan.displayname, chan.language, chan.logo, chan.current_rank, chan.twitchurl, chan.name_id) for chan in new_channels]
            try:
                cursor.executemany(sql, values)
                connection.commit()
                print(f"Added {len(new_channels)} new channels.")
            except Exception as e:
                print(f"Error occurred (addNewChannelToDb): {e}")
                connection.rollback()
        # for chan in scrapped_channels:
        #     if chan.name_id in non_existing_name_ids:
        #         print("Adding new channel:", chan.name_id)
        #         sql = "INSERT INTO Channels (DisplayName, Language, Logo, CurrentRank, TwitchUrl, NameId) VALUES (%s, %s, %s, %s, %s, %s)"
        #         values = (chan.displayname, chan.language, chan.logo, chan.current_rank, chan.twitchurl, chan.name_id)
        #         try:
        #             cursor.execute(sql, values)
        #             connection.commit()
        #         except Exception as e:
        #             print(f"Error occurred: {e}")
        #             connection.rollback()
        # finally:
    connection.close()
                
def updateChannelRankingLazily(scrapped_channels: List[ScrappedChannel]):
    connection = getConnection()
    with connection.cursor() as cursor:
        # A. Depriorities all old ones by pushing it down in Ranking
        # values = [(len(scrapped_channels), chan.name_id) for chan in scrapped_channels]
        sql = "UPDATE Channels SET CurrentRank = CurrentRank + %s"
        try:
            values = (len(scrapped_channels),) # Ensure that the value is passed as a tuple
            affected_count = cursor.execute(sql, values)
            print("Updating Ranks. affected_count:", str(affected_count))
            connection.commit()
        except Exception as e:
            print(f"Error occurred (updateChannelRankingLazily A): {e}")
            connection.rollback()

        # B. Set priroity for current & new round
        values = [(chan.current_rank, chan.name_id) for chan in scrapped_channels]
        sql = "UPDATE Channels SET CurrentRank = %s WHERE NameId = %s"
        try:
            cursor.executemany(sql, values)
            connection.commit()
        except Exception as e:
            print(f"Error occurred (updateChannelRankingLazily B): {e}")
            connection.rollback()

    connection.close()

def updateVodsDb(scrapped_channels: List[ScrappedChannel]):
    print("000000000000000000000000000000000000000")
    print("000000000     updateVodsDb    000000000")
    print("000000000000000000000000000000000000000")
    connection = getConnection()
    max_vods = int(env_varz.PREP_DB_UPDATE_VODS_NUM)
    with connection.cursor() as cursor:
        for chan in scrapped_channels:
            chan.print()
            links = chan.links[:max_vods] 
            vod_ids = [ link.split('/')[-1] for link in links]
            if len(vod_ids) == 0:
                continue
            placeholders = ', '.join(['%s'] * len(vod_ids))
            query = f"SELECT Id FROM Vods WHERE Id IN ({placeholders})"
            cursor.execute(query, vod_ids)

            # Get results
            existing_ids = [row[0] for row in cursor.fetchall()]
            non_existing_ids = set(vod_ids) - set(existing_ids)
            previous_existing_ids = set(existing_ids) - set(non_existing_ids)
            print("    (updateVodsDb) Channel: " + str(chan.name_id))
            print("    (updateVodsDb) Links: " + str(vod_ids))
            print("    (updateVodsDb) Updating priorities on IDs :", list(previous_existing_ids))
            print("    (updateVodsDb) Adding new IDs :", list(non_existing_ids))
            print("")

            # Add new vods to the Vods table
            if non_existing_ids:
                trans_status = "todo"            
                values = [(vod_id, chan.name_id, trans_status, idx) for idx, vod_id in enumerate(non_existing_ids)]
                sql = "INSERT INTO Vods (Id, ChannelNameId, TranscriptStatus, Priority, TodoDate) VALUES (%s, %s, %s, %s, NOW())"
                try:
                    cursor.executemany(sql, values)
                    connection.commit()  # Commit the transaction
                except Exception as e:
                    print(f"Error occurred (updateVodsDb) a: {e}")
                    connection.rollback()

            # Update the priority of vods. Recall priority essentially is the release date. eg, top-left to bottom-right https://www.twitch.tv/lolgeranimo/videos
            if previous_existing_ids:
                sql = "UPDATE Vods SET Priority = %s WHERE ID = %s  AND TranscriptStatus = 'todo'"
                values = [(idx, vod_id) for idx, vod_id in enumerate(previous_existing_ids)]
                try:
                    cursor.executemany(sql, values)
                    connection.commit()  # Commit the transaction
                except Exception as e:
                    print(f"Error occurred (updateVodsDb): {e}")
                    connection.rollback()
    connection.close()
    print("    (updateVodsDb) Completed update!")

# YYYY-MM-DD
# CREATE TABLE Rankings (
#     RankingId INT NOT NULL AUTO_INCREMENT,
#     ChannelNameId VARCHAR(255),
#     Ranking SMALLINT,
#     TodoDate DATETIME,

#     PRIMARY KEY (RankingID),
#     FOREIGN KEY (ChannelNameId) REFERENCES Channels(NameId)
# );


# CREATE TABLE Channels (
#     NameId VARCHAR(255),
#     DisplayName VARCHAR(255),
#     Language VARCHAR(255),
#     Logo VARCHAR(255),
#     CurrentRank VARCHAR(255),
#     TwitchUrl VARCHAR(255),
#     NumberOfVods INT,

#     PRIMARY KEY (NameId)
# );

##     Title VARCHAR(255), CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,

# CREATE TABLE Vods (
#     Id VARCHAR(255),
#     ChannelNameId VARCHAR(255),
#     Title VARCHAR(255),
#     Duration VARCHAR(255),
#     DurationString VARCHAR(255),
#     TranscriptStatus VARCHAR(255),
#     StreamDate DATETIME,
#     TodoDate DATETIME,
#     DownloadDate DATETIME,
#     TranscribeDate DATETIME,
#     S3Audio VARCHAR(255),
#     S3CaptionFiles JSON,
#     WebpageUrl VARCHAR(255),
#     Model VARCHAR(255),
#     Priority SMALLINT,
#     Thumbnail VARCHAR(255),
#     ViewCount VARCHAR(255),
    
#     PRIMARY KEY (Id),
#     FOREIGN KEY (ChannelNameId) REFERENCES Channels(NameId)
# );
# # This is the default below 
# # ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_0900_ai_ci;

# ALTER TABLE Vods MODIFY DownloadDate DATETIME;
# ALTER TABLE Vods ADD COLUMN DownloadDate DATETIME;
# ALTER TABLE Vods ADD COLUMN StreamDate DATETIME;
# ALTER TABLE Vods ADD COLUMN TodoDate DATETIME;
# ALTER TABLE Vods ADD COLUMN S3Link VARCHAR(255);
# ALTER TABLE Vods ADD COLUMN TranscribeDate DATETIME;
# ALTER TABLE Rankings ADD COLUMN TodoDate DATETIME;

# CREATE TABLE Channels (
#     DisplayName VARCHAR(255),
#     Language VARCHAR(255),
#     Logo VARCHAR(255),
#     CurrentRank VARCHAR(255),
#     TwitchUrl VARCHAR(255),
#     NameId VARCHAR(255),
#     NumberOfVods INT,

#     PRIMARY KEY (NameId)
# );


##################

# ALTER TABLE Rankings
# ADD Time TIME,
# ADD Datetime DATETIME

# ALTER TABLE Vods 
# ADD Id VARCHAR(255);
# ADD Title VARCHAR(255);
# ADD Duration VARCHAR(255);
# ADD DurationString VARCHAR(255);
# ADD ViewerCount VARCHAR(255);
# ADD WebpageUrl VARCHAR(255);
# ADD Timestamp VARCHAR(255);
# ADD S3CaptionFiles JSON;
