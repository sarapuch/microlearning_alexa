var mongoose = require('mongoose');
var Schema = mongoose.Schema;

/**
 * Schema creado para poder hacer debug sobre la api:
 *  -id_alumno: id_alexa o id_telegram o id_alumno de la plataforma
 *  -model: string que guarda los valores para poder llamar a defaultModel de ebisu
 *  -lastTest: string de la fecha en la que se realizó el último test
 */
var EbisuMLSchema = new Schema({
    id_alumno: { type: Number, required: true },
    model: { type: String },
    lastTest: { type: String }
});


module.exports = mongoose.model('ebisuML', EbisuMLSchema);

