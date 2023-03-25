// npm install aws-sdk
// npm install express

// auto reload
// nodemon .\apiBabyyyy.js
// nodemon .\apiBabyyyy.js
// nodemon .\apiBabyyyy.js
// nodemon .\apiBabyyyy.js

var express = require('express');
var app = express();
// import * as s3Stuff from './routes/s3.js';
const s3Stuff = require('./routes/s3.js');


// const myCron = require('./jobs/jobs'); // This calls cron
// const transcriptRoutes = require('./routes/transcriptRoutes');
// require("dotenv").config();
// app.use(transcriptRoutes)

const dbPass = process.env.DB_PASS;
var server = app.listen(4444, function () {
   var host = server.address().address
   var port = server.address().port
   
   console.log("Example app listening at http://%s:%s", host, port)
})

// app.get('/', async (req, res) => {
//     res.render('./transcripts/search', {title : 'Search'});
// })

// app.get('/', function (req, res) {
//   res.send('Hello World');
// })

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/pages/home.html');
});


app.get('/hi', (req, res) => {
    res.send('Hello, world!');
});

app.get('/data', (req, res) => {
    // res.status(200).json({
    res.json({
        message: 'Success',
        data: [1, 2, 3, 4, 5]
    });
});

// app.use((req, res) => {
//   res.status(404).sendFile('./views/404.html', {root: __dirname})
// })

app.get('/s3List', async (req, res) => {
  // res.status(200).json({
  
  // s3Stuff.fn2();
  let x = await s3Stuff.listBuckets()
  console.log("x")
  console.log("x")
  console.log("x")
  console.log(x)
  // res.send(x);
  res.json(x)
  // res.json({
  //     message: s3Stuff.fn1(),
  // });
});

app.get('/s3Render', async (req, res) => {

  let x = await s3Stuff.maxJsonifyContent()
  console.log("x")
  console.log("x")
  console.log("x")
  console.log(x)
  // res.send(x);
  res.json(x)
  // res.json({
  //     message: s3Stuff.fn1(),
  // });
});
