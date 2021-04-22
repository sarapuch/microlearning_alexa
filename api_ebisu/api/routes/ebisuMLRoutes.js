
module.exports = function(app) {
    var ebisuML = require('../controllers/ebisuMLController');

    /**
     * Rutas creadas para hacer debug de la api
     */
    app.route('/api/ebisuML/')
        .get(ebisuML.listStudents) //lista todos los alumnos encontrados en la base de datos
        .post(ebisuML.createStudent); //crea un alumno, se entiende que al crearlo ya ha realizado el cuestionario

    app.route('/api/ebisuML/:id_student')
        .put(ebisuML.updateStudent) //modifica los datos del alumno
        .delete(ebisuML.deleteStudent); //elimina los datos del alumno

    /**
     * Rutas creadas para el uso de Ebisu en específico
     */
    app.route('/api/ebisuML/:id_student/Recall') //Devuelve la probabilidad de que recuerde el temario específico
        .get(ebisuML.predictRecall);

    app.route('/api/ebisuML/:id_student/UpdateRecall')
        .get(ebisuML.updateRecall); //Con los resultados obtenidos, calcula la situación del alumno. Actualiza el modelo y la fecha del último cuestionario

    app.route('/api/ebisuML/:id_student/predictDate')
        .get(ebisuML.predictDate); //Devuelve el número de horas que faltan para llegar al % solicitado

};