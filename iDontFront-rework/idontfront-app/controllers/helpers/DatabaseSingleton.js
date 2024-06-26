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
        }
        return DatabaseSingleton.instance;
    }

    printHi() {
        console.log("process.env.DATABASE_HOST", process.env.DATABASE_HOST)
        console.log("process.env.DATABASE_USERNAME", process.env.DATABASE_USERNAME)
        console.log("process.env.DATABASE", process.env.DATABASE)
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

    async getChannelsForHomepage() {
        console.log("getting channels for homepage...")
        try {
            const sqlQuery = `
                SELECT *
                FROM Channels c
                WHERE EXISTS (
                    SELECT 1
                    FROM Vods v
                    WHERE v.ChannelNameId = c.NameId
                    AND v.TranscriptStatus = 'completed'
                ) ORDER BY CurrentRank ASC;`;
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
