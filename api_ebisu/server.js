var express = require('express'),
    app = express(),
    port = process.env.PORT || 3000,
    mongoose = require('mongoose'),
    EbisuML = require('./api/models/ebisuMLModel'),
    bodyParser = require('body-parser');

mongoose.Promise = global.Promise;
mongoose.connect('mongodb://localhost/Ebisudb', { useFindAndModify: false });

app.use(bodyParser.urlencoded({ extended:true }));
app.use(bodyParser.json());

var routes = require('./api/routes/ebisuMLRoutes');
routes(app);

app.use(function(req, res) {
    res.status(404).send({url: req.originalUrl + ' not found'})
});

app.listen(port);

console.log('API EbisuML server started on: '+port);