from models.ScrappedChannel import ScrappedChannel
from typing import List
from datetime import datetime

from dotenv import load_dotenv

import os
import MySQLdb


# load_dotenv()
import env_file as env_varz



def updateDb1(scrapped_channels: List[ScrappedChannel]):
    connection = MySQLdb.connect(
        host    = env_varz.DATABASE_HOST,
        user    = env_varz.DATABASE_USERNAME,
        passwd  = env_varz.DATABASE_PASSWORD,
        db      = env_varz.DATABASE,
        autocommit  = True,
        ssl_mode    = "VERIFY_IDENTITY",
        ssl         = { "ca": "C:/Users/BrodskiTheGreat/Documents/HeidiSQL/cacert-2023-08-22.pem" } # See https://planetscale.com/docs/concepts/secure-connections#ca-root-configuration to determine the path to your operating systems certificate file.
    )

    try:
        for chan in scrapped_channels:
            chan.print()
        addNewChannelToDb(scrapped_channels, connection)
        # addRankingsForTodayDb(scrapped_channels, connection) # This is optional
        updateVodsDb(scrapped_channels, connection)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()



def addRankingsForTodayDb(scrapped_channels: List[ScrappedChannel], connection):
    with connection.cursor() as cursor:
        for chan in scrapped_channels:
            print("Adding new Ranks:", chan.name_id, chan.current_rank)
            sql = "INSERT INTO Rankings (Date, Time, Datetime, ChannelNameId, Ranking)  VALUES(CURRENT_DATE(), CURRENT_TIME(), NOW(), %s, %s)"
            values = (chan.name_id, int(chan.current_rank))
            try:
                cursor.execute(sql, values)
                # connection.commit() # since autocommit we dont need line
            except Exception as e:
                print(f"Error occurred: {e}")
                connection.rollback()

def addNewChannelToDb(scrapped_channels: List[ScrappedChannel], connection):
    with connection.cursor() as cursor:
        # Make SQL Query
        name_ids = [chn.name_id for chn in scrapped_channels]
        formatted_ids = ', '.join([f"'{str(name)}'" for name in name_ids])
        query = f"SELECT NameId FROM Channels WHERE NameId IN ({formatted_ids})"

        cursor.execute(query)

        # Get results
        existing_name_ids = [row[0] for row in cursor.fetchall()]
        non_existing_name_ids = set(name_ids) - set(existing_name_ids)

        print("Existing IDs:", existing_name_ids)
        print("Non-existing IDs:", list(non_existing_name_ids))

        # Add new channels to database
        for chan in scrapped_channels:
            if chan.name_id in non_existing_name_ids:
                print("Adding new channel:", chan.name_id)
                sql = "INSERT INTO Channels (DisplayName, Language, Logo, CurrentRank, TwitchUrl, NameId) VALUES (%s, %s, %s, %s, %s, %s)"
                values = (chan.displayname, chan.language, chan.logo, chan.current_rank, chan.twitchurl, chan.name_id)
                try:
                    cursor.execute(sql, values)
                except Exception as e:
                    print(f"Error occurred: {e}")
                    connection.rollback()
                
def updateVodsDb(scrapped_channels: List[ScrappedChannel], connection):
    max_vods = int(env_varz.YTDL_VIDS_PER_CHANNEL)
    print("max_vods")
    print(max_vods)
    print(type(max_vods))
    with connection.cursor() as cursor:
        for chan in scrapped_channels:
            print("0000000000000000000000000000000000000000000000")
            print("000000000     updateVodsDb (loop)    000000000")
            print("0000000000000000000000000000000000000000000000")
            # Prepare a parameterized query for IN clause
            links = chan.links[:max_vods] 
            vod_ids = [ link.split('/')[-1] for link in links]

            placeholders = ', '.join(['%s'] * len(vod_ids))
            # query = f"SELECT NameId FROM Channels WHERE NameId IN ({placeholders})"
            query = f"SELECT Id FROM Vods WHERE Id IN ({placeholders})"
            print("Query:", query)
            print("Values:", vod_ids)
            cursor.execute(query, vod_ids)

            # Get results
            existing_ids = [row[0] for row in cursor.fetchall()]
            non_existing_ids = set(vod_ids) - set(existing_ids)
            previous_existing_ids = set(existing_ids) - set(non_existing_ids)
            print("---------------------------")
            print("Existing IDs:", existing_ids)
            print("Non-existing IDs:", list(non_existing_ids))
            print("Previous-existing IDs:", list(previous_existing_ids))
            print("---------------------------")

            # Add new vods to the TODO list
            if non_existing_ids:
                trans_status = "todo"            
                insert_values = [(vod_id, chan.name_id, trans_status, idx) for idx, vod_id in enumerate(non_existing_ids)]
                sql = "INSERT INTO Vods (Id, ChannelNameId, TranscriptStatus, Priority, TodoDate) VALUES (%s, %s, %s, %s, NOW())"
                print("insert_values: ", insert_values)
                print("sql: ", sql )
                print("values: ", insert_values)
                try:
                    cursor.executemany(sql, insert_values)
                    connection.commit()  # Commit the transaction
                except Exception as e:
                    print(f"Error occurred: {e}")
                    connection.rollback()

            # Update the priority of vods
            print("-")
            if previous_existing_ids:
                sql = "UPDATE Vods SET Priority = %s WHERE ID = %s  AND TranscriptStatus = 'todo'"
                values = [(idx, vod_id) for idx, vod_id in enumerate(previous_existing_ids)]
                print("previous_existing_ids", previous_existing_ids)
                print("values", values)
                try:
                    cursor.executemany(sql, values)
                    connection.commit()  # Commit the transaction
                except Exception as e:
                    print(f"Error occurred: {e}")
                    connection.rollback()


# YYYY-MM-DD
# CREATE TABLE Rankings (
#     RankingId INT NOT NULL AUTO_INCREMENT,
#     ChannelNameId VARCHAR(255),
#     Date DATE, 
#     Time TIME,
#     Datetime DATETIME,

#     Ranking SMALLINT,
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

# CREATE TABLE Vods (
#     Id VARCHAR(255),
#     ChannelNameId VARCHAR(255),

#     Title VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
#     Duration VARCHAR(255),
#     DurationString VARCHAR(255),
#     ViewCount VARCHAR(255),
#     WebpageUrl VARCHAR(255),
#     Thumbnail VARCHAR(255)
#     UploadDate DATETIME,
#     TranscriptStatus VARCHAR(255),
#     TodoDate DATETIME
#     S3Link VARCHAR(255)

#     PRIMARY KEY (Id),
#     FOREIGN KEY (ChannelNameId) REFERENCES Channels(NameId)
# ); 

# ALTER TABLE Vods CHANGE UploadDate UploadDate DATETIME;
# ALTER TABLE Vods DROP COLUMN Timestamp;

# ALTER TABLE Vods ADD COLUMN Thumbnail VARCHAR(255);
# ALTER TABLE Vods ADD COLUMN TodoDate DATETIME;
# ALTER TABLE Vods ADD COLUMN S3Link VARCHAR(255);

# ALTER TABLE Vods CHANGE S3Link S3Audio VARCHAR(255);







# CREATE TABLE Channels (
#     ID INT NOT NULL AUTO_INCREMENT,
#     DisplayName VARCHAR(255),
#     Language VARCHAR(255),
#     Links VARCHAR(255),
#     Logo VARCHAR(255),
#     CurrentRank VARCHAR(255),
#     TwitchUrl VARCHAR(255),
#     NameId VARCHAR(255),
#     NumberOfVods INT,

#     PRIMARY KEY (ID)
# );

# CREATE TABLE Vods (
#     ID INT NOT NULL AUTO_INCREMENT,
#     TwitchUrl VARCHAR(255),
#     TranscriptUrl VARCHAR(255),

#     ChannelID INT,
#     PRIMARY KEY (ID),
#     FOREIGN KEY (ChannelID) REFERENCES Channels(ID)
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
# ADD UploadDate VARCHAR(255);
# ADD Timestamp VARCHAR(255);


# CREATE TABLE Todo (
#     ID INT NOT NULL AUTO_INCREMENT,
#     Status ENUM('todo', 'in progress', 'completed'),

#     VodID INT,
#     ChannelID INT,
#     PRIMARY KEY (ID),
#     FOREIGN KEY (VodID) REFERENCES Vods(ID),
#     FOREIGN KEY (ChannelID) REFERENCES Channels(ID)
# );
