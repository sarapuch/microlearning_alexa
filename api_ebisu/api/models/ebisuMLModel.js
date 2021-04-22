var mongoose = require('mongoose');
var Schema = mongoose.Schema;

/**
 * Schema creado para poder hacer debug sobre la api:
 *  -id_student: id_alexa o id_telegram o id_alumno de la plataforma
 *  -alpha: parámetro del modelo de ebisu
 *  -beta: parámetro del modelo de ebisu
 *  -halflife: parámetro del modelo de ebisu. Indica el número de horas en el que el porcentaje decae al 50%
 *  -lastTest: string de la fecha en la que se realizó el último test
 */
var EbisuMLSchema = new Schema({
    id_student: { type: Number, required: true },
    alpha: { type: Number },
    beta: { type: Number },
    halflife: { type: Number }, 
    lastTest: { type: String }
});


module.exports = mongoose.model('ebisuML', EbisuMLSchema);

