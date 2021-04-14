
module.exports = function(app) {
    var ebisuML = require('../controllers/ebisuMLController');

    /**
     * Rutas creadas para hacer debug de la api
     */
    app.route('/api/ebisuML/')
        .get(ebisuML.listAlumno) //lista todos los alumnos encontrados en la base de datos
        .post(ebisuML.createAlumno); //crea un alumno, se entiende que al crearlo ya ha realizado el cuestionario

    app.route('/api/ebisuML/:id_alumno')
        .put(ebisuML.updateAlumno) //modifica los datos del alumno
        .delete(ebisuML.deleteAlumno); //elimina los datos del alumno

    /**
     * Rutas creadas para el uso de Ebisu en específico
     */
    app.route('/api/ebisuML/:id_alumno/Recall') //Devuelve la probabilidad de que recuerde el temario específico
        .put(ebisuML.predictRecall);

    app.route('/api/ebisuML/:id_alumno/UpdateRecall')
        .put(ebisuML.updateRecall); //Con los resultados obtenidos, calcula la situación del alumno. Actualiza el modelo y la fecha del último cuestionario

    app.route('/api/ebisuML/:id_alumno/predictDate')
        .put(ebisuML.predictDate); //Devuelve el número de horas que faltan para llegar al % solicitado

};