from datetime import datetime
import traceback
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
from models.ScrappedChannel import ScrappedChannel
from utils.emailer import sendEmail
from typing import List
import env_file as env_varz
import MySQLdb
import os

def getConnection():
    connection = MySQLdb.connect(
        db      = env_varz.DATABASE,
        host    = env_varz.DATABASE_HOST,
        user    = env_varz.DATABASE_USERNAME,
        passwd  = env_varz.DATABASE_PASSWORD,
        port    = int(env_varz.DATABASE_PORT),
        autocommit  = False,
        # ssl_mode    = "VERIFY_IDENTITY",
        # ssl         = { "ca": env_varz.SSL_FILE } # See https://planetscale.com/docs/concepts/secure-connections#ca-root-configuration to determine the path to your operating systems certificate file.
    )
    return connection


def addRankingsForTodayDb(scrapped_channels: List[ScrappedChannel]):
    connection = getConnection()
    with connection.cursor() as cursor:
        values = [(chan.name_id, int(chan.current_rank)) for chan in scrapped_channels]
        sql = "INSERT INTO Rankings (TodoDate, ChannelNameId, Ranking) VALUES (NOW(), %s, %s)"
        print("  (addRankingsForTodayDb) Adding new Ranks:", str(values))
        print("  (addRankingsForTodayDb) Adding new sql:", str(sql))
        try:
            with connection.cursor() as cursor:
                cursor.executemany(sql, values)  # Batch insert
            connection.commit()
        except Exception as e:
            print(f" (addRankingsForTodayDb) Error occurred: {e}")
            stack_trace = traceback.format_exc()
            print(stack_trace)
            connection.rollback()
    connection.close()

def getNewOldChannelsFromDB(scrapped_channels: List[ScrappedChannel]):
    connection = getConnection()
    with connection.cursor() as cursor:
        scrapped_name_ids = [chn.name_id for chn in scrapped_channels]
        formatted_ids = ', '.join([f"'{str(name)}'" for name in scrapped_name_ids])
        query = f"SELECT * FROM Channels;"

        cursor.execute(query)

        # Get results
        channels_all_in_db_aux = cursor.fetchall()
        channels_all_in_db: List[ScrappedChannel] = []
        for tup in channels_all_in_db_aux:
            channel = ScrappedChannel(
                name_id = tup[0],
                displayname = tup[1],
                language = tup[2],
                # links = tup[]
                logo = tup[3],
                current_rank = tup[4],
                twitchurl = tup[5],
                viewminutes = tup[6],
                streamedminutes = tup[7],
                maxviewers = tup[8],
                avgviewers = tup[9],
                followers = tup[10],
                followersgained = tup[11],
                partner = tup[12],
                affiliate = tup[13],
                mature = tup[14],
                previousviewminutes = tup[15],
                previousstreamedminutes = tup[16],
                previousmaxviewers = tup[17],
                previousavgviewers = tup[18],
                previousfollowergain = tup[19],
                # daysMeasured = tup[20]
            )
            channels_all_in_db.append(channel)
        matching_channels = [ch1 for ch1 in channels_all_in_db if any(ch1.name_id == ch2.name_id for ch2 in scrapped_channels)]

        scrapped_id = {ch.name_id for ch in scrapped_channels}
        all_channels_minus_scrapped = [ch1 for ch1 in channels_all_in_db if ch1.name_id not in scrapped_id]

        print(" (getNewOldChannelsFromDB) matching_channels")
        print([ch.name_id for ch in matching_channels])
        print(" (getNewOldChannelsFromDB) channels_all_in_db")
        print([ch.name_id for ch in channels_all_in_db])
        print("scrapped_channels")
        print("scrapped_channels")
        print("scrapped_channels")
        print("scrapped_channels")
        print([ch.name_id for ch in scrapped_channels])
        print(" (getNewOldChannelsFromDB) all_channels_minus_scrapped")
        print([ch.name_id for ch in all_channels_minus_scrapped])
        
        vip_list = [channel for channel in scrapped_channels if channel.name_id in ("lolgeranimo", "nmplol")]
        return all_channels_minus_scrapped + vip_list


def updateChannelDataByHtmlIteratively(all_channels_minus_scrapped: List[ScrappedChannel]):
    all_channels_minus_scrapped
    cnt = -1
    for chan in all_channels_minus_scrapped:
        cnt = cnt + 1
        url = f'https://sullygnome.com/channel/{chan.name_id}/{env_varz.PREP_SULLY_DAYS}'
        print(f"-------  {cnt} (sully data) --------")
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            text_data = response.content.decode('utf-8') 
            if response.url == "https://sullygnome.com/": # redirected
                msg = f"url={url} - cnt={cnt} \n They redirected! response.url is now: " + response.url
                print(msg)
                print(msg)
                print(msg)
                sendEmail(msg)
                # docker builder prune
                continue
        
            soup = BeautifulSoup(text_data, 'html.parser')
            data1 = soup.select("#pageHeaderMiddle .MiddleSubHeaderContainer .MiddleSubHeaderItemValue")
            data2 = soup.select(".InfoStatPanelContainerTop .InfoStatPanelWrapper .InfoStatPanelTL")
            
            chan.followers  = data1[0].get_text().replace(",", "")
            chan.partner    = True if data1[2].get_text().lower() == "partnered" else False
            chan.mature     = True if data1[3].get_text().lower() == "yes" else False

            chan.avgviewers         = data2[0].get_text().replace(",", "")
            chan.viewminutes        = int(data2[1].get_text().replace(",", "")) * 60 # HOURS
            chan.followersgained    = data2[2].get_text().replace(",", "")
            chan.maxviewers         = data2[3].get_text().replace(",", "")
            chan.streamedminutes    = int(data2[4].get_text().replace(",", "")) * 60 #HOURS
            chan.print()

        else:
            print('An error has occurred.')

def addNewChannelToDb(scrapped_channels: List[ScrappedChannel]):
    connection = getConnection()
    days_measured = int(env_varz.PREP_SULLY_DAYS)
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
            sql = "INSERT INTO Channels (DisplayName, Language, Logo, CurrentRank, TwitchUrl, NameId, ViewMinutes, StreamedMinutes, MaxViewers, AvgViewers, Followers, FollowersGained, Partner, Affiliate, Mature, PreviousViewMinutes, PreviousStreamedMinutes, PreviousMaxViewers, PreviousAvgViewers, PreviousFollowerGain, DaysMeasured) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = [(chan.displayname, chan.language, chan.logo, chan.current_rank, chan.twitchurl, chan.name_id, chan.viewminutes, chan.streamedminutes, chan.maxviewers, chan.avgviewers, chan.followers, chan.followersgained, chan.partner, chan.affiliate, chan.mature, chan.previousviewminutes, chan.previousstreamedminutes, chan.previousmaxviewers, chan.previousavgviewers, chan.previousfollowergain, days_measured) for chan in new_channels]
            try:
                cursor.executemany(sql, values)
                connection.commit()
                print(f"Added {len(new_channels)} new channels.")
            except Exception as e:
                print(f"Error occurred (addNewChannelToDb): {e}")
                connection.rollback()
            finally:
                connection.close()

def updateChannelRankingLazily(scrapped_channels: List[ScrappedChannel]):
    connection = getConnection()
    with connection.cursor() as cursor:
        # A. Depriorities all old ones by pushing it down in Ranking
        sql = "UPDATE Channels SET CurrentRank = CurrentRank + %s"
        print("len(scrapped_channels)",len(scrapped_channels))
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
        print("UPDATING THESE!")
        print(values)
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
            print("----------------------")
            # chan.print()
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
                    connection.commit()
                except Exception as e:
                    print(f"Error occurred (updateVodsDb) a: {e}")
                    connection.rollback()

            # Update the priority of vods. Recall priority essentially is the release date. eg, top-left to bottom-right https://www.twitch.tv/lolgeranimo/videos
            if previous_existing_ids:
                sql = "UPDATE Vods SET Priority = %s WHERE ID = %s  AND TranscriptStatus = 'todo'"
                values = [(idx, vod_id) for idx, vod_id in enumerate(previous_existing_ids)]
                try:
                    cursor.executemany(sql, values)
                    connection.commit()
                except Exception as e:
                    print(f"Error occurred (updateVodsDb): {e}")
                    connection.rollback()
    if connection.open:
        connection.close()
    print("    (updateVodsDb) Completed update!")

def updateChannelWatchStats(scrapped_channels: List[ScrappedChannel]):
    connection = getConnection()
    days_measured = int(env_varz.PREP_SULLY_DAYS)
    sql = """
        UPDATE Channels
        SET 
            ViewMinutes = %s,
            StreamedMinutes = %s,
            MaxViewers = %s,
            AvgViewers = %s,
            Followers = %s,
            FollowersGained = %s,
            Partner = %s,
            Affiliate = %s,
            Mature = %s,
            PreviousViewMinutes = %s,
            PreviousStreamedMinutes = %s,
            PreviousMaxViewers = %s,
            PreviousAvgViewers = %s,
            PreviousFollowerGain = %s,
            DaysMeasured = %s
        WHERE NameId  = %s
    """
    values = [(chan.viewminutes, chan.streamedminutes, chan.maxviewers, chan.avgviewers, chan.followers, chan.followersgained, chan.partner, chan.affiliate, chan.mature, chan.previousviewminutes, chan.previousstreamedminutes, chan.previousmaxviewers, chan.previousavgviewers, chan.previousfollowergain, days_measured, chan.name_id) for chan in scrapped_channels]
    print('updateChannelWatchStats() - updating this many: ', len(values))
    # print(values)
    try:
        with connection.cursor() as cursor:
            cursor.executemany(sql, values)
        connection.commit()  # Commit the transaction
    except Exception as e:
        print(f"Error occurred (updateChannelWatchStats): {e}")
        connection.rollback()
    finally:
        connection.close()
    print("    (updateChannelWatchStats) Completed update!")

def deleteOldTodos():
    print("    (deleteOldTodos) running...")
    connection = getConnection()
    sql = """
        DELETE FROM Vods
        WHERE Id IN (
            SELECT Id
            FROM (
                SELECT Id
                FROM Vods
                WHERE (TranscriptStatus = 'todo' OR TranscriptStatus = 'unknown')
                AND TodoDate <= CURDATE() - INTERVAL 30 DAY
            ) AS subquery
        );

    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            affected_rows = cursor.rowcount 
            print("    (deleteOldTodos) deleted affected_rows:", affected_rows)
        connection.commit()  # Commit the transaction
    except Exception as e:
        print(f"Error occurred (deleteOldTodos): {e}")
        connection.rollback()
    finally:
        connection.close()



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

# ALTER TABLE Channels
# ADD COLUMN ViewMinutes INT,
# ADD COLUMN StreamedMinutes INT,
# ADD COLUMN MaxViewers INT,
# ADD COLUMN AvgViewers INT,
# ADD COLUMN Followers INT,
# ADD COLUMN FollowersGained INT,
# ADD COLUMN Partner BOOLEAN,
# ADD COLUMN Affiliate BOOLEAN,
# ADD COLUMN Mature BOOLEAN,
# ADD COLUMN PreviousViewMinutes INT,
# ADD COLUMN PreviousStreamedMinutes INT,
# ADD COLUMN PreviousMaxViewers INT,
# ADD COLUMN PreviousAvgViewers INT,
# ADD COLUMN PreviousFollowerGain INT;
# ADD COLUMN DaysMeasured INT;

# !!!!!!!!!!!!!! IMPORTANT !!!!!!!!!!!!!!!!!!!!!
# ALTER TABLE Channels DROP COLUMN NumberOfVods;



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


# ALTER TABLE Vods ADD COLUMN S3Thumbnails JSON;