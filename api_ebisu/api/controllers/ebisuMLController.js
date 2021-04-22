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
exports.listStudents = function(req, res) {
    EbisuML.find({}, function(err, students) {
        if (err)
            res.send(err);
        res.json(students);
    })
}

/**
 * Crea con los datos recibidos un alumno
 * @param {*} req 
 * @param {*} res 
 */
exports.createStudent = function(req, res) {
    
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
exports.updateStudent= function(req, res) {
    EbisuML.findOneAndUpdate({id_student: req.params.id_student}, req.body, {new: true}, function(err, alumno) {
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
exports.deleteStudent = function(req, res) {
    EbisuML.deleteOne({id_student: req.params.id_student}, function(err, ok) {
        if(err) res.send(err);
        res.send({message: "deleted"})
    })
}

//funciones creadas para la API

/**
 * Recibe como parámetro la id_student, y como argumento de query actualDate. De la base de datos saca estos argumentos:
 *  -lastTest: fecha en la que se realizó el último test
 *  -alpha: parámetro de modelo de ebisu
 *  -beta: parámetro de modelo de ebisu
 *  -halflife: parámetro de modelo de ebisu. Indica el número de horas en el que el porcentaje decae al 50%
 * 
 * @param {*} req 
 * @param {*} res recall: porcentaje que recuerda el alumno sobre x factor
 */
exports.predictRecall = function(req, res) {
    //id_student || actualDate    
    
    //obtenemos de la base de datos lastTest y parámetros del modelo (alpha, beta y halflife)
    var md = EbisuML.findOne({id_student: req.params.id_student}).exec(function(err, doc) {
        var student = doc.toObject()
        var lastTest = student.lastTest;
        var alpha = student.alpha
        var beta = student.beta
        var halflife = student.halflife
        
        //Ajustamos los parámetros que pide predictRecall, diffDates en horas y el modelo
        var diffDates = calculateDiffDates(req.query.actualDate, lastTest) //llamada a función del cálculo de horas
        var model = ebisu.defaultModel(halflife, alpha, beta)

        var predictedRecall = ebisu.predictRecall(model, diffDates, true);
        
        res.send({predictedRecall: Number(predictedRecall)*100+'%'})
        
    })  
     
};

/**
 * Recibe como parámetro la id_student y como argumento de query actualDate, total de preguntas y total de aciertos. De la base de datos
 * saca estos argumentos:
 *  -lastTest: fecha en la que se realizó el último test
 *  -alpha: parámetro de modelo de ebisu
 *  -beta: parámetro de modelo de ebisu
 *  -halflife: parámetro de modelo de ebisu. Indica el número de horas en el que el porcentaje decae al 50%
 * Una vez obtenido el nuevo modelo, se actualizan en la base de datos lastTest, alpha, beta y halflife. 
 * 
 * @param {*} req 
 * @param {*} res alumno actualizado
 */
exports.updateRecall = function(req, res) {
    //id_student || actualDate, successes, total

    //obtenemos de la base de datos lastTest, alpha, beta y halflife
    var md = EbisuML.findOne({id_student: req.params.id_student}).exec(function(err, doc) {
        var student = doc.toObject()
        var lastTest = student.lastTest;
        var alpha = student.alpha;
        var beta = student.beta;
        var halflife = student.halflife
              
        //Ajustamos los parámetros que pide updateRecall, diffDates en horas y el modelo
        var diffDates = calculateDiffDates(req.query.actualDate, lastTest)
        var model = ebisu.defaultModel(halflife, alpha, beta)
        var updatedModel = ebisu.updateRecall(model, Number(req.query.success), Number(req.query.total), diffDates);
        
        //Obtenemos de el modelo de ebisu los parametros
        updatedModel = updatedModel.toString().replace('[','').replace(']','') //ajustamos string
        updatedModel_split = updatedModel.split(',')
        alpha = Number(updatedModel_split[0])
        beta = Number(updatedModel_split[1])
        halflife = Number(updatedModel_split[2])
        
        //Actualizamos en la base de datos los nuevos parámetros del usuario: lastTest, alpha, beta y halflife
        EbisuML.findOneAndUpdate({id_student: req.params.id_student}, {lastTest: req.query.actualDate, alpha: alpha, beta: beta, halflife: halflife}, {new: true}, function(err, alumno) {
            if (err)
                res.send(err);
            res.json(alumno);    
        });
    })
}

/**
 * Recibe por parámetro id_student, y como parámetro de query percent. Este es el porcentaje de recuerdo.
 * De la base de datos se saca este parámetro:
 *  -alpha: parámetro de modelo de ebisu
 *  -beta: parámetro de modelo de ebisu
 *  -halflife: parámetro de modelo de ebisu. Indica el número de horas en el que el porcentaje decae al 50%
 * Una vez realizada la llamada, devuelve el número de horas que faltan para llegar a ese porcentaje
 * @param {*} req 
 * @param {*} res time_decay diferencia en horas
 */
exports.predictDate = function(req, res) {
    //id_student || percent
    var percent = Number(req.query.percent);

    //obtenemos de la base de datos alpha, beta y halflife
    var md = EbisuML.findOne({id_student: req.params.id_student}).exec(function(err, doc) {
        var student = doc.toObject();
        var alpha = student.alpha;
        var beta = student.beta
        var halflife = student.halflife

        //calculamos modelo
        var model = ebisu.defaultModel(halflife, alpha, beta);
        
        var time_decay = ebisu.modelToPercentileDecay(model, percent, true);
        res.send({time_decay: time_decay});
    })
    
}

/**
 * Función temporal. Recibe actualDate y lastDate y devuelve el numero de horas de diferencia entre ambas. Como actualDate y
 * lastDate son strings, debe parsearlos para convertirlos en Date. Una vez obtenidas las dos fechas, simplemente se restan
 * y pasamos el resultado, en ms, a horas. 
 * @param {*} actualDate string. formato yyyy-MM-ddTHH:mm:ss
 * @param {*} lastDate string. formato yyyy-MM-ddTHH:mm:ss
 * @returns diffDates => diferencia en horas entre las dos fechas
 */
function calculateDiffDates (actualDate, lastDate) {
    //transformamos de una string a Date 
    var actualDate = actualDate.split("T");
    var date = actualDate[0].split("-");
    var time = actualDate[1].split(":");
    var actualDate = new Date(Number(date[0]), Number(date[2])-1, Number(date[1]), Number(time[0])+1, Number(time[1]), Number(time[2]));

    //transformamos de una string a Date 
    var lastDate = lastDate.split("T");
    var date = lastDate[0].split("-");
    var time = lastDate[1].split(":");
    var lastDate = new Date(Number(date[0]), Number(date[2])-1, Number(date[1]), Number(time[0])+1, Number(time[1]), Number(time[2]));

    //pasamos el resultado de la resta de ms a horas
    var diffDates = ((actualDate - lastDate)/(1000*60*60)).toFixed(1);

    return diffDates

}


