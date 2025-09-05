from datetime import datetime
import traceback
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
from models.ScrappedChannel import ScrappedChannel
from utils.emailer import sendEmail
from utils.logging_config import LoggerConfig
from typing import List
import env_file as env_varz
import MySQLdb
import os
import logging

def logger():
    pass

logger: logging.Logger = LoggerConfig("micro").get_logger()

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

# NOT USED
def addRankingsForTodayDb(scrapped_channels: List[ScrappedChannel]):
    connection = getConnection()
    with connection.cursor() as cursor:
        values = [(chan.name_id, int(chan.current_rank)) for chan in scrapped_channels]
        sql = "INSERT INTO Rankings (TodoDate, ChannelNameId, Ranking) VALUES (NOW(), %s, %s)"
        logger.debug("Adding new Ranks:" +  str(values))
        logger.debug("Adding new sql:" +  str(sql))
        try:
            with connection.cursor() as cursor:
                cursor.executemany(sql, values)  # Batch insert
            connection.commit()
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            stack_trace = traceback.format_exc()
            logger.error(stack_trace)
            connection.rollback()
    connection.close()

def getNewOldChannelsFromDB(scrapped_channels: List[ScrappedChannel]):
    connection = getConnection()
    with connection.cursor() as cursor:
        scrapped_name_ids = [chn.name_id for chn in scrapped_channels]
        formatted_ids = ', '.join([f"'{str(name)}'" for name in scrapped_name_ids])
        logger.debug("formatted_ids" +  formatted_ids)
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

        logger.debug("")
        logger.debug("scrapped_channels:")
        logger.debug([ch.name_id for ch in scrapped_channels])
        logger.debug("")
        logger.debug("matching_channels (no one new: the scrapped_channels has no new entries)")
        logger.debug([ch.name_id for ch in matching_channels])
        logger.debug("")
        logger.debug("channels_all_in_db:")
        logger.debug([ch.name_id for ch in channels_all_in_db])
        logger.debug("")
        logger.debug("scrapped_channels:")
        logger.debug([ch.name_id for ch in scrapped_channels])
        logger.debug("")
        logger.debug("all_channels_minus_scrapped:")
        logger.debug([ch.name_id for ch in all_channels_minus_scrapped])

        logger.debug("")
        return all_channels_minus_scrapped
        return channels_all_in_db
        return all_channels_minus_scrapped + vip_list


def updateChannelDataByHtmlIteratively(all_channels_plus_scrapped: List[ScrappedChannel]):
    all_channels_plus_scrapped
    cnt = -1
    for chan in all_channels_plus_scrapped:
        cnt = cnt + 1
        if env_varz.PREP_SULLY_DAYS == "7":
            url = f'https://sullygnome.com/channel/{chan.name_id}'
        else:
            url = f'https://sullygnome.com/channel/{chan.name_id}/{env_varz.PREP_SULLY_DAYS}'
        logger.info(f"-------  {cnt} (sully data) --------")
        logger.info(url)
        headers = {
            "accept-language": "en-US,en;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            text_data = response.content.decode('utf-8') 
            if response.url == "https://sullygnome.com/": # redirected
                subject = f"Preper {os.getenv('ENV')} - Failed selenium scrap on a channel"
                msg = f"Attempted but failed url={url} - cnt={cnt} \nThey redirected! response.url is now: " + response.url
                logger.error(msg)
                sendEmail(subject, msg)
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
            logger.debug("    " +  chan.name_id)
            chan.print()

        else:
            logger.debug('An error has occurred.')

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

        logger.debug("Existing IDs:" +  existing_name_ids)
        logger.debug("New IDs: " + str(new_channels))

        # Add new channels to database
        if new_channels:
            sql = "INSERT INTO Channels (DisplayName, Language, Logo, CurrentRank, TwitchUrl, NameId, ViewMinutes, StreamedMinutes, MaxViewers, AvgViewers, Followers, FollowersGained, Partner, Affiliate, Mature, PreviousViewMinutes, PreviousStreamedMinutes, PreviousMaxViewers, PreviousAvgViewers, PreviousFollowerGain, DaysMeasured) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = [(chan.displayname, chan.language, chan.logo, chan.current_rank, chan.twitchurl, chan.name_id, chan.viewminutes, chan.streamedminutes, chan.maxviewers, chan.avgviewers, chan.followers, chan.followersgained, chan.partner, chan.affiliate, chan.mature, chan.previousviewminutes, chan.previousstreamedminutes, chan.previousmaxviewers, chan.previousavgviewers, chan.previousfollowergain, days_measured) for chan in new_channels]
            try:
                cursor.executemany(sql, values)
                connection.commit()
                logger.debug(f"MONEY 💰 Added {len(new_channels)} new channels.")
            except Exception as e:
                logger.error(f"Error occurred (addNewChannelToDb): {e}")
                logger.error(traceback.format_exc())
                connection.rollback()
            finally:
                connection.close()

def updateChannelRankingLazily(scrapped_channels: List[ScrappedChannel]):
    connection = getConnection()
    with connection.cursor() as cursor:
        # A. Depriorities all old ones by pushing it down in Ranking
        sql = "UPDATE Channels SET CurrentRank = CurrentRank + %s"
        logger.debug("len(scrapped_channels)" + len(scrapped_channels))
        try:
            values = (len(scrapped_channels),) # Ensure that the value is passed as a tuple
            affected_count = cursor.execute(sql, values)
            logger.debug("MONEY 💰 Updating Ranks. affected_count:" +  str(affected_count))
            connection.commit()
        except Exception as e:
            logger.error(f"Error occurred (updateChannelRankingLazily A): {e}")
            connection.rollback()

        # B. Set priroity for current & new round
        values = [(chan.current_rank, chan.name_id) for chan in scrapped_channels]
        sql = "UPDATE Channels SET CurrentRank = %s WHERE NameId = %s"
        logger.debug("UPDATING THESE!")
        logger.debug(values)
        try:
            cursor.executemany(sql, values)
            connection.commit()
        except Exception as e:
            logger.error(f"Error occurred (updateChannelRankingLazily B): {e}")
            connection.rollback()
    connection.close()

def updateVodsDb(scrapped_channels: List[ScrappedChannel]):
    logger.info("000000000000000000000000000000000000000")
    logger.info("000000000     updateVodsDb    000000000")
    logger.info("000000000000000000000000000000000000000")
    connection = getConnection()
    # max_vods = int(env_varz.PREP_SELENIUM_NUM_VODS_PER)
    max_vods = int(env_varz.NUM_VOD_PER_CHANNEL)
    with connection.cursor() as cursor:
        for chan in scrapped_channels:
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
            logger.debug("Channel: " + str(chan.name_id))
            logger.debug("Links: " + str(vod_ids))
            logger.debug("Updating priorities on IDs :" +  str((previous_existing_ids)))
            logger.debug("Adding new IDs :" +  str(non_existing_ids))
            logger.debug("")

            # Add new vods to the Vods table
            if non_existing_ids:
                trans_status = "todo"            
                values = [(vod_id, chan.name_id, trans_status, idx) for idx, vod_id in enumerate(non_existing_ids)]
                sql = "INSERT INTO Vods (Id, ChannelNameId, TranscriptStatus, Priority, TodoDate) VALUES (%s, %s, %s, %s, NOW())"
                try:
                    cursor.executemany(sql, values)
                    connection.commit()
                except Exception as e:
                    logger.error(f"Error occurred (updateVodsDb) a: {e}")
                    connection.rollback()

            # Update the priority of vods. Recall priority essentially is the release date. eg, top-left to bottom-right https://www.twitch.tv/geranimo/videos
            if previous_existing_ids:
                sql = "UPDATE Vods SET Priority = %s WHERE ID = %s  AND TranscriptStatus = 'todo'"
                values = [(idx, vod_id) for idx, vod_id in enumerate(previous_existing_ids)]
                try:
                    cursor.executemany(sql, values)
                    connection.commit()
                except Exception as e:
                    logger.error(f"Error occurred (updateVodsDb): {e}")
                    connection.rollback()
    if connection.open:
        connection.close()
    logger.debug("    (updateVodsDb) Completed update!")

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
    logger.debug('updating this many: ' + str(len(values)))
    # logger.debug(values)
    try:
        with connection.cursor() as cursor:
            cursor.executemany(sql, values)
        connection.commit()  # Commit the transaction
    except Exception as e:
        logger.error(f"Error occurred (updateChannelWatchStats): {e}")
        connection.rollback()
    finally:
        connection.close()
    logger.debug("Completed update!")

def deleteOldTodos():
    INTERVAL = 20
    logger.debug("running...")
    connection = getConnection()
    sql = """
        DELETE FROM Vods
        WHERE Id IN (
            SELECT Id
            FROM (
                SELECT Id
                FROM Vods
                WHERE (TranscriptStatus = 'todo' OR TranscriptStatus = 'unknown' OR TranscriptStatus = 'too_big' OR TranscriptStatus = 'transcribing')
                AND TodoDate <= CURDATE() - INTERVAL 10 DAY
            ) AS subquery
        );

    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            affected_rows = cursor.rowcount 
            logger.info("    (deleteOldTodos) deleted affected_rows:" + str(affected_rows))
        connection.commit()  # Commit the transaction
    except Exception as e:
        logger.error(f"Error occurred (deleteOldTodos): {e}")
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

# UPDATE Vods
# SET TranscriptStatus = 'deleted_old'
# WHERE TranscriptStatus = 'completed'
#   AND TranscribeDate < '2024-06-01';
