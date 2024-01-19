const mysql = require('mysql2'); // mysql2 supports promise-based interface
const path = require('path');
const fs = require('fs');
const Channel = require("../../models/Channel")
const Vod = require("../../models/Vod")


console.log("process.env.NODE_ENV: ", process.env.NODE_ENV)

class DatabaseSingleton {
    constructor() {
        if (!DatabaseSingleton.instance) {
            console.log("DB SINGLETON HAS BEEN INIT!")
            this.pool = mysql.createPool({
                connectionLimit: 10, 
                host: process.env.DATABASE_HOST,
                user: process.env.DATABASE_USERNAME,
                password: process.env.DATABASE_PASSWORD,
                database: process.env.DATABASE,
                ssl: {
                    ca: fs.readFileSync('../../cacert-2023-08-22.pem'),
                }
            }).promise();
            DatabaseSingleton.instance = this;
        }
        console.log("db singleton, BAM!")
        return DatabaseSingleton.instance;
    }

    printHi() {
        console.log("hello from the singelton babyyyyyyyyyyy")
        console.log("process.env.DATABASE_HOST", process.env.DATABASE_HOST)
        console.log("process.env.DATABASE_USERNAME", process.env.DATABASE_USERNAME)
        console.log("process.env.DATABASE_PASSWORD", process.env.DATABASE_PASSWORD)
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
            // throw error;
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
            // throw error;
        } 
    }

    async getVods(nameId) {
        try {
            const sqlQuery = `
                SELECT *
                FROM Vods
                WHERE ChannelNameId = ? AND TranscriptStatus = 'completed'
                ORDER BY StreamDate ASC;`;
            const promiseVods = this.pool.query(sqlQuery, [nameId])
            return promiseVods;
        } catch (error) {
            console.error('Error retrieving vods: ', error);
            // throw error;
        } 
    }

    async getChannelsForHomepage() {
        try {
            const sqlQuery = `
                SELECT *
                FROM Channels
                ORDER BY CurrentRank ASC;`;
            const [results, fields] = await this.pool.query(sqlQuery);
            let resultChannelObj = results.map( chan => new Channel(chan))
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
            throw err; // Rethrow the error for the caller to handle
        }
    }

    // Optionally: Method to close the connection pool
    async close() {
        await this.pool.end();
    }




    // async getVodsX(nameId) {
    //     try {
    //         // const sqlQuery = `
    //         //     SELECT V.*, C.DisplayName, C.Language, C.Logo, C.CurrentRank, C.TwitchUrl
    //         //     FROM Vods V
    //         //     INNER JOIN Channels C ON V.ChannelNameId = C.NameId
    //         //     WHERE V.ChannelNameId = ? AND V.TranscriptStatus = 'completed'
    //         //     ORDER BY V.StreamDate ASC;`
    //         const sqlQueryVods = `
    //             SELECT *
    //             FROM Vods
    //             WHERE ChannelNameId = ? AND TranscriptStatus = 'completed'
    //             ORDER BY StreamDate ASC;`;
    //         const sqlQueryChan = `
    //             SELECT *
    //             FROM Channels
    //             WHERE NameId = ?;`;
    //         // const [resultsVods, fields] = await this.pool.query(sqlQueryVods, [nameId])
    //         // const [resultsChan, fields2] = await this.pool.query(sqlQueryChan, [nameId])
    //         // let resultChannelObj = results.map( chan => new Vod(chan))
    //         // console.log(resultChannelObj)
            
    //         const promiseVods = this.pool.query(sqlQueryVods, [nameId])
    //         const promiseChan = this.pool.query(sqlQueryChan, [nameId])
    //         // const [resultsVods_w_fields, resultsChan_w_fields] = await Promise.all([promiseVods, promiseChan]);
    //         const [[resultsVods,fields1], [resultsChan,fields2]] = await Promise.all([promiseVods, promiseChan]);
    //         // [resultsVods, fields]
    //         console.log('Vods results:', resultsVods);
    //         console.log('Channels results:', resultsChan);
    //         console.log("results vods1chan")
    //         console.log("results vods1chan")
    //         console.log("results vods1chan")
    //         console.log("results vods1chan")
    //         // console.log(results)
    //         return results;
    //         // return resultChannelObj;
    //     } catch (error) {
    //         console.error('Error retrieving channels: ', error);
    //         // throw error;
    //     } 
    // }







}

module.exports = DatabaseSingleton;

// Example usage:
// const db = new DatabaseSingleton();
// db.query('SELECT * FROM your_table').then(results => {
//     console.log(results);
// }).catch(err => {
//     console.error(err);
// });
