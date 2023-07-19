const express = require('express');
const path = require('path');
// const ejs = require('ejs');
const configs = require("./configs");
const mainRoutes = require('./routes/mainRoutes');

const app = express();

app.set('view engine', 'ejs');
app.set('views', './views') // this line not needed b/c views is by default
app.use(express.static(path.join(__dirname, 'public')));
app.set('views', path.join(__dirname, '/views'));

app.locals.configs = configs

// Body Parser Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: false }));


// app.get('/', (req, res) => {
//     res.render('index', { title: 'Home' });
// });

app.use(mainRoutes)

const PORT = process.env.PORT || 3333;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
