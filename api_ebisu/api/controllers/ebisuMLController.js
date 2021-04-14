var ebisu = require('ebisu-js');
const { update } = require('../models/ebisuMLModel');

var mongoose = require('mongoose'),
    EbisuML = mongoose.model('ebisuML');

//funciones creadas para hacer debug de la api
/**
 * Lista a los alumnos que existen en la base de datos
 * @param {*} req 
 * @param {*} res 
 */
exports.listAlumno = function(req, res) {
    EbisuML.find({}, function(err, alumnos) {
        if (err)
            res.send(err);
        res.json(alumnos);
    })
}

/**
 * Crea con los datos recibidos un alumno
 * @param {*} req 
 * @param {*} res 
 */
exports.createAlumno = function(req, res) {
    var defaultModel = ebisu.defaultModel(req.body.model);
    console.log(defaultModel);
    req.body.model = defaultModel.toString();
    var new_alumno = new EbisuML(req.body);
    new_alumno.save(function(err, alumnos) {
        if (err)
            res.send(err);
        res.json(alumnos);
    });
};

/**
 * Actualiza los datos de un alumno
 * @param {*} req 
 * @param {*} res 
 */
exports.updateAlumno = function(req, res) {
    EbisuML.findOneAndUpdate({id_alumno: req.params.id_alumno}, req.body, {new: true}, function(err, alumno) {
        if (err)
            res.send(err);
        res.json(alumno);
    });
};

/**
 * Elimina de la base de datos a un alumno
 * @param {*} req 
 * @param {*} res 
 */
exports.deleteAlumno = function(req, res) {
    EbisuML.deleteOne({id_alumno: req.params.id_alumno}, function(err, ok) {
        if(err) res.send(err);
        res.send({message: "deleted"})
    })
}

//funciones creadas para la API

/**
 * Recibe como parámetro la id_alumno, y como argumento de body fechaActual. De la base de datos saca estos argumentos:
 *  -lastTest: fecha en la que se realizó el último test
 *  -model: string con los valores adecuados para llamar a ebisu.defaultModel
 * Actualmente las fechas se guardan en String para poder ver los cambios facilmente. En el producto final, estas fechas
 * se calcularán con la fecha actual, es decir fechaX = new Date(). Gran Parte del código se encarga de traducir los string a fechas.
 * @param {*} req 
 * @param {*} res recall: porcentaje que recuerda el alumno sobre x factor
 */
exports.predictRecall = function(req, res) {
    //id_alumno || fechaActual

    //Calculo fecha Actual yyyy-dd-MMTHH:mm:ss
    var fechahora = req.body.fechaActual.split("T");
    var fecha = fechahora[0].split("-");
    var hora = fechahora[1].split(":");
    var fechaActual = new Date(Number(fecha[0]), Number(fecha[2])-1, Number(fecha[1]), Number(hora[0])+1, Number(hora[1]), Number(hora[2]));
    
    //obtenemos de la base de datos lastTest y model
    var md = EbisuML.findOne({id_alumno: req.params.id_alumno}).exec(function(err, doc) {
        var alumno = doc.toObject()
        var lastTest = alumno.lastTest;
        var model = alumno.model.split(',');

        //Calculo fecha Anterior yyyy-dd-MMTHH:mm:ss
        fechahora = lastTest.split("T")
        fecha = fechahora[0].split("-");
        hora = fechahora[1].split(":");
        var fechaAnterior = new Date(Number(fecha[0]), Number(fecha[2])-1, Number(fecha[1]), Number(hora[0])+1, Number(hora[1]), Number(hora[2]));
        
        //Ajustamos los parámetros que pide predictRecall, diffDates en horas y el modelo
        var diffDates = ((fechaActual - fechaAnterior)/(1000*60*60)).toFixed(1);
        var modelo = ebisu.defaultModel(Number(model[2]), Number(model[0]), Number(model[1]))
        
        var predictedRecall = ebisu.predictRecall(modelo, Number(diffDates), true);
        
        res.send({predictedRecall: Number(predictedRecall)*100+'%'})
        
    })  
     
};

/**
 * Recibe como parámetro la id_alumno y como argumento de body fechaActual, total de preguntas y total de aciertos. De la base de datos
 * saca estos argumentos:
 *  -lastTest: fecha en la que se realizó el último test
 *  -model: string con los valores adecuados para llamar a ebisu.defaultModel
 * Una vez obtenido el nuevo modelo, se actualizan en la base de datos lastTest y model. 
 * Actualmente las fechas se guardan en String para poder ver los cambios facilmente. En el producto final, estas fechas
 * se calcularán con la fecha actual, es decir fechaX = new Date(). Gran Parte del código se encarga de traducir los string a fechas.
 * @param {*} req 
 * @param {*} res alumno actualizado
 */
exports.updateRecall = function(req, res) {
    //id_alumno || fechaActual, successes, total

    //Calculo fecha Actual yyyy-dd-MMTHH:mm:ss
    var fechahora = req.body.fechaActual.split("T");
    var fecha = fechahora[0].split("-");
    var hora = fechahora[1].split(":");
    var fechaActual = new Date(Number(fecha[0]), Number(fecha[2])-1, Number(fecha[1]), Number(hora[0])+1, Number(hora[1]), Number(hora[2]));
    
    //obtenemos de la base de datos lastTest y model
    var md = EbisuML.findOne({id_alumno: req.params.id_alumno}).exec(function(err, doc) {
        var alumno = doc.toObject()
        var lastTest = alumno.lastTest;
        var model = alumno.model.split(',');
        
        //Calculo fecha Anterior yyyy-dd-MMTHH:mm:ss
        fechahora = lastTest.split("T")
        fecha = fechahora[0].split("-");
        hora = fechahora[1].split(":");
        var fechaAnterior = new Date(Number(fecha[0]), Number(fecha[2])-1, Number(fecha[1]), Number(hora[0])+1, Number(hora[1]), Number(hora[2]));
              
        //Ajustamos los parámetros que pide updateRecall, diffDates en horas, el modelo
        var diffDates = ((fechaActual - fechaAnterior)/(1000*60*60)).toFixed(1);
        var modelo = ebisu.defaultModel(Number(model[2]), Number(model[0]), Number(model[1]))
        
        var updatedModel = ebisu.updateRecall(modelo, Number(req.body.succes), Number(req.body.total), Number(diffDates));
        
        //Actualizamos en la base de datos model y lastTest
        updatedModel = updatedModel.toString().replace('[','').replace(']','') //ajustamos string
        EbisuML.findOneAndUpdate({id_alumno: req.params.id_alumno}, {lastTest: req.body.fechaActual, model: updatedModel}, {new: true}, function(err, alumno) {
            if (err)
                res.send(err);
            res.json(alumno);    
        });
    })
}

/**
 * Recibe por parámetro id_alumno, y como parámetro de body percent. Este es el porcentaje de olvido/recuerdo.
 * De la base de datos se saca este parámetro:
 *  -model: string con los valores adecuados para llamar a ebisu.defaultModel
 * Una vez realizado la llamada, devuelve el número de horas que faltan para llegar a ese porcentaje
 * @param {*} req 
 * @param {*} res tOlvido diferencia en horas
 */
exports.predictDate = function(req, res) {
    //percent id_alumno
    var percent = Number(req.body.percent);

    //obtenemos de la base de datos model
    var md = EbisuML.findOne({id_alumno: req.params.id_alumno}).exec(function(err, doc) {
        var alumno = doc.toObject();
        var model = alumno.model.split(',');

        //ajuste de parámetro
        var modelo = ebisu.defaultModel(Number(model[2]), Number(model[0]), Number(model[1]));
        
        var tOlvido = ebisu.modelToPercentileDecay(modelo, percent, true);
        res.send({tOlvido: tOlvido});
    })
    
}


