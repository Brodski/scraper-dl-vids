from datetime import datetime
import traceback
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
from models.ScrappedChannel import ScrappedChannel
from utils.emailer import sendEmail
from utils.logging_config import loggerX
from typing import List
# import env_file as env_varz
from env_file import env_varz
import MySQLdb
import os
import logging
from models.MetadataP import MetadataP


metadata_p = MetadataP()

def logger():
    pass

# logger: logging.Logger = LoggerConfig("micro").get_logger()
logger: logging.Logger = loggerX

def getConnection():
    connection = MySQLdb.connect(
        db      = env_varz.DATABASE,
        host    = env_varz.DATABASE_HOST,
        user    = env_varz.DATABASE_USERNAME,
        passwd  = env_varz.DATABASE_PASSWORD,
        port    = int(env_varz.DATABASE_PORT),
        autocommit  = False,
        charset="utf8mb4"
    )
    return connection

def getExistingChannelsFromDB(scrapped_channels: List[ScrappedChannel]):
    connection = getConnection()
    with connection.cursor() as cursor:
        query = f"SELECT * FROM Channels;"

        cursor.execute(query)

        # Get results
        channels_all_in_db_aux = cursor.fetchall()
        channels_all_in_db: List[ScrappedChannel] = []
        for tup in channels_all_in_db_aux:
            channel = ScrappedChannel(
                name_id                 = tup[0],
                displayname             = tup[1],
                language                = tup[2],
                logo                    = tup[3],
                current_rank            = tup[4],
                twitchurl               = tup[5],
                viewminutes             = tup[6],
                streamedminutes         = tup[7],
                maxviewers              = tup[8],
                avgviewers              = tup[9],
                followers               = tup[10],
                followersgained         = tup[11],
                partner                 = tup[12],
                affiliate               = tup[13],
                mature                  = tup[14],
                previousviewminutes     = tup[15],
                previousstreamedminutes = tup[16],
                previousmaxviewers      = tup[17],
                previousavgviewers      = tup[18],
                previousfollowergain = tup[19],
                # daysMeasured = tup[20]
            )
            channels_all_in_db.append(channel)
        
        matching_channels = [ch1 for ch1 in channels_all_in_db if any(ch1.name_id == ch2.name_id for ch2 in scrapped_channels)]

        scrapped_id = {ch.name_id for ch in scrapped_channels}
        all_channels_minus_scrapped = [ch1 for ch1 in channels_all_in_db if ch1.name_id not in scrapped_id]

        logger.debug("-")
        logger.debug("scrapped_channels:")
        logger.debug([ch.name_id for ch in scrapped_channels])
        logger.debug("-")
        logger.debug("matching_channels (no one new: the scrapped_channels has no new entries)")
        logger.debug([ch.name_id for ch in matching_channels])
        logger.debug("-")
        logger.debug("channels_all_in_db:")
        logger.debug([ch.name_id for ch in channels_all_in_db])
        logger.debug("-")
        logger.debug("all_channels_minus_scrapped:")
        logger.debug([ch.name_id for ch in all_channels_minus_scrapped])

        logger.debug("-")
        return all_channels_minus_scrapped

def getNewChannelsNotInDb(scrapped_channels: List[ScrappedChannel]):
    connection = None
    new_channels = None
    try:
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
            new_channels: List[ScrappedChannel] = [chan for chan in scrapped_channels if chan.name_id not in existing_name_ids]

            logger.debug("Existing IDs:" +  str(existing_name_ids))
            logger.debug("New IDs: " + str(new_channels))
    except Exception as e:
        logger.error(f"Error occurred (addNewChannelToDb): {e}")
        logger.error(traceback.format_exc())
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()
    return new_channels

def addNewChannelToDb(new_channels: List[ScrappedChannel]):
    connection = None
    if new_channels:
        try:
            connection = getConnection()
            days_measured = int(env_varz.PREP_SULLY_DAYS)

            with connection.cursor() as cursor:
                # Add new channels to database
                sql = "INSERT INTO Channels (DisplayName, Language, Logo, CurrentRank, TwitchUrl, NameId, ViewMinutes, StreamedMinutes, MaxViewers, AvgViewers, Followers, FollowersGained, Partner, Affiliate, Mature, PreviousViewMinutes, PreviousStreamedMinutes, PreviousMaxViewers, PreviousAvgViewers, PreviousFollowerGain, DaysMeasured) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = [(chan.displayname, chan.language, chan.logo, chan.current_rank, chan.twitchurl, chan.name_id, chan.viewminutes, chan.streamedminutes, chan.maxviewers, chan.avgviewers, chan.followers, chan.followersgained, chan.partner, chan.affiliate, chan.mature, chan.previousviewminutes, chan.previousstreamedminutes, chan.previousmaxviewers, chan.previousavgviewers, chan.previousfollowergain, days_measured) for chan in new_channels]

                cursor.executemany(sql, values)
                connection.commit()
                logger.debug(f"MONEY 💰 Added {len(new_channels)} new channels:")
                for chan in new_channels:
                    logger.debug(f"  New: " + chan.displayname)
                metadata_p.new_channels = new_channels
        except Exception as e:
            logger.error(f"Error occurred (addNewChannelToDb): {e}")
            logger.error(traceback.format_exc())
            if connection:
                connection.rollback()
        finally:
            if connection:
                connection.close()
        return new_channels
    else:
        logger.debug("No new channels to add.")


def updateChannelDataByHtmlIteratively(all_channels_plus_scrapped: List[ScrappedChannel]):
    all_channels_plus_scrapped
    cnt = -1
    metadata_p.num_channels_updated_via_sully = len(all_channels_plus_scrapped)
    metadata_p.num_channels_updated_via_sully_actual = 0
    for chan in all_channels_plus_scrapped:
        cnt = cnt + 1
        if env_varz.PREP_SULLY_DAYS == "30":
            url = f'https://sullygnome.com/channel/{chan.name_id}'
        else:
            url = f'https://sullygnome.com/channel/{chan.name_id}/{env_varz.PREP_SULLY_DAYS}'
        logger.info(f"-------  {cnt} (updating every channel in the DB via sully) --------")
        logger.info(url)
        headers = {
            "accept-language": "en-US,en;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            text_data = response.content.decode('utf-8') 
            if response.url == "https://sullygnome.com/": # ❌ -> redirected
                ################################
                # ERROR SOLUTION - WRITE EMAIL #
                # silent error b/c redirect    # 
                ################################
                ### SUBJECT
                subject = f"Preper {os.getenv('ENV')} - (Redirect) Failed selenium scrap on a channel"
                ### BODY
                msg = f"Attempted but failed url={url} - cnt={cnt} \n"
                msg = msg + f"They redirected! response.url is now: " + response.url + "\n"
                msg = msg + f"⚠ Must update manually!\n"
                msg = msg + f"1. Google search missing channel. eg '{chan.name_id} twitch' \n"
                msg = msg + f"2. Go to HeidiSQL -> find NameId='{chan.name_id}' -> update 'NameID' and maybe 'DisplayName'.\n"
                msg = msg + f"3. Done \n"
                logger.error(msg)
                sendEmail(subject, msg)
                continue
            else: # ✅
                ########################
                # UPDATE STREAMER INFO #
                ########################
                # TODO?? i could catch errors with css/html updates better, and notify me about changes.
                soup = BeautifulSoup(text_data, 'html.parser')
                data1 = soup.select("#pageHeaderMiddle .MiddleSubHeaderContainer .MiddleSubHeaderItemValue")
                data2 = soup.select(".InfoStatPanelContainerTop .InfoStatPanelWrapper .InfoStatPanelTL")
                data3 = soup.select(".PageHeaderInner .PageHeaderMiddleTop img")
                
                chan.followers  = data1[0].get_text().replace(",", "")
                chan.partner    = True if data1[2].get_text().lower() == "partnered" else False
                chan.mature     = True if data1[3].get_text().lower() == "yes" else False

                chan.avgviewers         = data2[0].get_text().replace(",", "")
                chan.viewminutes        = int(data2[1].get_text().replace(",", "")) * 60 # HOURS
                chan.followersgained    = data2[2].get_text().replace(",", "")
                chan.maxviewers         = data2[3].get_text().replace(",", "")
                chan.streamedminutes    = int(data2[4].get_text().replace(",", "")) * 60 #HOURS
                chan.logo               = data3[0].attrs["src"]

                metadata_p.num_channels_updated_via_sully_actual += 1
                logger.debug(chan.name_id)
                # chan.print()

        else:
            subject = f"Preper {os.getenv('ENV')} - (Error) Failed selenium scrap on a channel"
            ### BODY
            msg = f"Some error occured :("
            msg = msg + f"Attempted but failed url={url} - cnt={cnt} \n"
            msg = msg + f"status_code = " + str(response.status_code) + "\n"
            msg = msg + "url: " +    str(response.url) + "\n"
            msg = msg + "headers: "+ str(dict(response.headers)) + "\n"
            msg = msg + "body: " +   str(response.text[:500])  # avoid logging huge payload)s
            logger.error(msg)
            sendEmail(subject, msg)
            continue

def updateChannelRankingLazily(scrapped_channels: List[ScrappedChannel]):
    connection = getConnection()
    logger.debug("len(scrapped_channels): " + str(len(scrapped_channels)))
    with connection.cursor() as cursor:
        ### A. Depriorities all old ones by pushing it down in Ranking ###
        sql = "UPDATE Channels SET CurrentRank = CurrentRank + %s"
        try:
            values = (len(scrapped_channels),) # must be tuple
            affected_count = cursor.execute(sql, values)
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
    max_vods = int(env_varz.PREP_NUM_VOD_PER_CHANNEL)
    with connection.cursor() as cursor:
        for chan in scrapped_channels:
            chan: ScrappedChannel = chan
            if chan.name_id not in metadata_p.vods_updated:
                metadata_p.vods_updated[chan.name_id] = {}

            links = chan.links[:max_vods] 
            vod_ids = [ link.split('/')[-1] for link in links]
            link_prio_map = {link: i for i, link in enumerate(vod_ids)} # hacky trick to make the vod_ids have a prioity, eg vod order, 1st vod is prioritized, 2nd, ect
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
            logger.debug("Updating priorities on IDs (already in DB): " +  str((previous_existing_ids)))
            logger.debug("Adding new IDs :" +  str(non_existing_ids))
            logger.debug("-")

            # Add new vods to the Vods table
            if non_existing_ids:
                trans_status = "todo"
                #                                      priority = link_prio_map[vod_id] = vod order, left to right
                #                                                    ↓
                values = [(vod_id, chan.name_id, trans_status, link_prio_map[vod_id]) for idx, vod_id in enumerate(non_existing_ids)]
                sql = "INSERT INTO Vods (Id, ChannelNameId, TranscriptStatus, Priority, TodoDate) VALUES (%s, %s, %s, %s, NOW())"
                try:
                    cursor.executemany(sql, values)
                    connection.commit()

                    metadata_p.vods_updated[chan.name_id]["new"] = non_existing_ids # non_existing_ids is List
                except Exception as e:
                    logger.error(f"Error occurred (updateVodsDb) a: {e}")
                    connection.rollback()

            # Update the priority of vods. Recall priority essentially is the release date. eg, top-left to bottom-right https://www.twitch.tv/geranimo/videos
            if previous_existing_ids:
                sql = "UPDATE Vods SET Priority = %s WHERE ID = %s  AND TranscriptStatus = 'todo'"
                values = [(link_prio_map[vod_id], vod_id) for idx, vod_id in enumerate(previous_existing_ids)]
                try:
                    cursor.executemany(sql, values)
                    connection.commit()
                    metadata_p.vods_updated[chan.name_id]["prev_existing"] = previous_existing_ids
                except Exception as e:
                    logger.error(f"Error occurred (updateVodsDb): {e}")
                    connection.rollback()
    if connection.open:
        connection.close()
    logger.debug("Completed update!")

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
    logger.debug("running...")
    connection = getConnection()
    days = 10
    sql = f"""
        DELETE FROM Vods
        WHERE Id IN (
            SELECT Id
            FROM (
                SELECT Id
                FROM Vods
                WHERE (TranscriptStatus = 'todo'
                    OR TranscriptStatus = 'unknown'
                    OR TranscriptStatus = 'too_big'
                    OR TranscriptStatus = 'downloading'
                    OR TranscriptStatus = 'transcribing')
                AND TodoDate <= CURDATE() - INTERVAL {days} DAY
            ) AS subquery
        );
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            affected_rows = cursor.rowcount 
            logger.info("    (deleteOldTodos) deleted affected_rows:" + str(affected_rows))
            metadata_p.deleted_olds_num = str(affected_rows)
        connection.commit()  # Commit the transaction
    except Exception as e:
        logger.error(f"Error occurred (deleteOldTodos): {e}")
        connection.rollback()
    finally:
        connection.close()


# For some reason, we get entries in Channels that have no Vods transcribed
def deleteOldDeadChannels(new_channels: List[ScrappedChannel]):
    # if env_varz.ENV == "prod":
    #     return
    logger.debug("new_channels:")
    for chan in new_channels:
        chan: ScrappedChannel = chan
        logger.debug(chan.name_id)
    try:
        connection = getConnection()
        with connection.cursor() as cursor:
            
            new_channels  = [] if new_channels is None else new_channels
            chan_name_ids = []
            # chan_name_ids = ["geranimo", "evelone2004", "ohnepixel", "loltyler1", "valorant"]

            chan_name_ids = [chan.name_id for chan in new_channels]
            ids = ",".join(["%s"] * len(chan_name_ids)) if chan_name_ids else "NULL"

            ### 1. Select everything in Channels that doesnt exist from our current scrape (scrapped_channels)
            ### 2. Find the intersection where at least 1 vod exists in Vods
            # can replace DELETE with like "SELECT *" to safe test
            sql = f"""
                DELETE FROM Channels
                WHERE (NameId NOT IN ({ids}) OR {len(chan_name_ids) == 0})
                AND NOT EXISTS (
                    SELECT 1
                    FROM Vods v
                    WHERE v.ChannelNameId = Channels.NameId
                );
            """
            logger.debug("DELETE sql")
            logger.debug(sql)
            logger.debug(chan_name_ids)
            cursor.execute(sql, chan_name_ids)
            logger.debug(f"Deleted {cursor.rowcount} rows from Channels")
    except Exception as e:
        logger.error(f"Error occurred (deleteOldTodos): {e}")
        connection.rollback()
    finally:
        connection.close()



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
