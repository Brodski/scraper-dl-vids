const mysql = require('mysql2'); // mysql2 supports promise-based interface
const path = require('path');
const fs = require('fs');
const Vod = require(path.resolve(__dirname, "../../models/Vod"))
const Channel = require(path.resolve(__dirname, "../../models/Channel"))
// `../../` does not work on the lambda docker 🤷🏿, eg `const Channel = require("../../models/Channel")`

class DatabaseSingleton {
    constructor() {
        if (!DatabaseSingleton.instance) {
            console.log("DB SINGLETON HAS BEEN INIT!")
            // const certPath = path.resolve(__dirname, '../../cacert-2023-08-22.pem');
            this.pool = mysql.createPool({
                connectionLimit: 10, 
                database: process.env.DATABASE,
                host: process.env.DATABASE_HOST,
                user: process.env.DATABASE_USERNAME,
                password: process.env.DATABASE_PASSWORD,
                port: process.env.DATABASE_PORT,
                // ssl: {
                //     ca: fs.readFileSync(certPath),
                // }
            }).promise();
            DatabaseSingleton.instance = this;
            console.log("process.env.DATABASE_HOST", process.env.DATABASE_HOST)
            console.log("process.env.DATABASE_USERNAME", process.env.DATABASE_USERNAME)
            console.log("process.env.DATABASE", process.env.DATABASE)
        }
        return DatabaseSingleton.instance;
    }

    async getVodById(vodId) {
        try {
            const sqlQuery = `
                SELECT *
                FROM Vods
                WHERE Id = ?;`;
            const promiseVod = this.pool.query(sqlQuery, [vodId])
            return promiseVod;
        } catch (error) {
            console.error('Error retrieving the vod: ', error);
        } 
    }
    async getChannel(nameId) {
        try {
            const sqlQuery = `
                SELECT *
                FROM Channels
                WHERE NameId = ?;`;
            const promiseChan = this.pool.query(sqlQuery, [nameId])
            return promiseChan;
        } catch (error) {
            console.error('Error retrieving the channel: ', error);
        } 
    }

    async getVods(nameId) {
        try {
            const sqlQuery = `
                SELECT *
                FROM Vods
                WHERE ChannelNameId = ? AND TranscriptStatus = 'completed'
                ORDER BY StreamDate DESC;`;
            const promiseVods = this.pool.query(sqlQuery, [nameId])
            return promiseVods;
        } catch (error) {
            console.error('Error retrieving vods: ', error);
        } 
    }

    async getChannelsMetadataHomepage() {
        try {
            const sqlQuery = `
            SELECT 
                ChannelNameId, 
                COUNT(*) AS EntryCount,
                SUM(CASE WHEN TranscriptStatus = 'completed ' THEN 1 ELSE 0 END) AS CompletedCount
            FROM 
                Vods
            WHERE 
                StreamDate >= DATE_SUB(NOW(), INTERVAL 14 DAY)
            GROUP BY 
                ChannelNameId;
            `
            const [results, fields] = await this.pool.query(sqlQuery);
            let resultChannelObj = results.map( chan => new Channel(chan));
            resultChannelObj.sort( (a,b) => {
                // first sort by viewMinutes, then by peviouwViewMinutes, then by followers
                return (b.viewMinutes - a.viewMinutes) || (b.previousViewMinutes - a.previousViewMinutes) ||  (b.followers - a.followers)
            })
            return resultChannelObj;
        } catch (error) {
            console.error('Error retrieving channels: ', error);
            // throw error;
        } 

    }

    async getChannelsForHomepage() {
        try {
            // const sqlQuery = `
            //     SELECT *
            //     FROM Channels c
            //     WHERE EXISTS (
            //         SELECT 1
            //         FROM Vods v
            //         WHERE v.ChannelNameId = c.NameId
            //         AND v.TranscriptStatus = 'completed'
            //     ) ORDER BY CurrentRank ASC;`;

            // 1 Query and aggregate "Completed" transcripts and aggregate broadcasts
            // 2 Query from Channels where at least 1 vod has a complted Transcript
            const sqlQuery = `
                SELECT 
                    c.*, 
                    IFNULL(v.EntryCount, 0) AS EntryCount, 
                    IFNULL(v.CompletedCount, 0) AS CompletedCount
                FROM 
                    Channels c
                LEFT JOIN 
                    (
                        SELECT 
                            ChannelNameId, 
                            COUNT(*) AS EntryCount,
                            SUM(CASE WHEN TranscriptStatus = 'completed' THEN 1 ELSE 0 END) AS CompletedCount
                        FROM 
                            Vods
                        WHERE 
                            StreamDate >= DATE_SUB(NOW(), INTERVAL 14 DAY)
                        GROUP BY 
                            ChannelNameId
                    ) v 
                ON 
                    c.NameId = v.ChannelNameId
                WHERE 
                    EXISTS (
                        SELECT 1
                        FROM Vods v2
                        WHERE v2.ChannelNameId = c.NameId
                        AND v2.TranscriptStatus = 'completed'
                    )
                ORDER BY 
                    c.CurrentRank ASC;
            `

            const [results, fields] = await this.pool.query(sqlQuery);
            let resultChannelObj = results.map( chan => new Channel(chan));
            resultChannelObj.sort( (a,b) => {
                // first sort by viewMinutes, then by peviouwViewMinutes, then by followers
                return (b.viewMinutes - a.viewMinutes) || (b.previousViewMinutes - a.previousViewMinutes) ||  (b.followers - a.followers)
            })

            console.log("resultChannelObj")
            console.log("resultChannelObj")
            console.log("resultChannelObj")
            console.log("resultChannelObj")
            console.log("resultChannelObj")
            console.log("resultChannelObj")
            console.log("resultChannelObj")
            console.log("resultChannelObj")
            console.log("resultChannelObj")
            console.log("resultChannelObj")
            console.log("resultChannelObj")
            console.log("resultChannelObj")
            console.log(resultChannelObj)
            return resultChannelObj;
        } catch (error) {
            console.error('Error retrieving channels: ', error);
            // throw error;
        } 
    }

    async query(sqlQuery) {
        try {
            // Get a connection from the pool and execute the query
            const [results, fields] = await this.pool.query(sqlQuery);
            console.log('Query results: ', results);
            return results;
        } catch (err) {
            console.error('Error in query: ', err);
            throw err; 
        }
    }

    async close() {
        await this.pool.end();
    }




}

module.exports = DatabaseSingleton;
