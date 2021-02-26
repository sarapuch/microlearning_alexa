# -*- coding: utf-8 -*-


import logging
import requests
import json
import ask_sdk_core.utils as ask_utils
import os
from ask_sdk_s3.adapter import S3Adapter
s3_adapter = S3Adapter(bucket_name = os.environ["S3_PERSISTENCE_BUCKET"])

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.response import Response
from ask_sdk_model.interfaces.audioplayer import (PlayDirective, PlayBehavior, AudioItem, Stream, AudioItemMetadata, StopDirective)

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

GENERAL_MANAGER = "http://castor.det.uvigo.es:7030/general_manager"
STUDENTS = "http://castor.det.uvigo.es:7000/students/"

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Bienvenido al servicio de microlearning. Necesito tu nombre, apellido y fecha de nacimiento."

        ask_output = "Primero preséntate. Necesito tu nombre, apellido y fecha de nacimiento."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class HasAuthLaunchRequestHandler(AbstractRequestHandler):
    """Handler for launch if it was requested before"""
    def can_handle(self, handler_input):
        #extract data and checks if it exists
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("name" in attr and "surname" in attr)

        return attributes_are_present and ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        attr = handler_input.attributes_manager.persistent_attributes
        name = attr["name"]
        surname = attr["surname"]

        speak_output = 'Bienvenido de nuevo, {name} {surname}'.format(name = name, month = month)
        handler_input.response_builder.speak(speak_output)
        return handler_input.response_builder.response

class getNameIntentHandler(AbstractRequestHandler):
    """Handler for getName Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("getNameIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        name = slots["name"].value
        surname = slots["surname"].value
        date = slots["date"].value

        #recogemos id_device
        sys_object = handler_input.request_envelope.context.system
        id_device = sys_object.device.device_id

        #guardamos datos
        attributes_manager = handler_input.attributes_manager
        name_attributes = {
            "name": name,
            "surname": surname
        }
        attributes_manager.persistence_attributes = name_attributes
        attributes_manager.save_persistent_attributes()

        #envio api
        url = "http://castor.det.uvigo.es:7000/students/identification_alexa/"+name+"/"+surname+"/"+date+"/"+id_device

        response = requests.get(url)

        speak_output = ''
        if response.status_code == 200:
            speak_output = 'Se ha identificado correctamente'
        else:
            speak_output = 'Hola {name} {surname}. Su codigo de error es {codigo}'.format(name = name, surname = surname, codigo = response.status_code)


        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("  Tienes que pedir la lista de unidades")
                .response
        )

class listUnitIDIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("listUnitIDIntent")(handler_input)

    def handle(self, handler_input):

        url = GENERAL_MANAGER + '/get_units'
        response_api = requests.get(url)
        #speak_output = f"Lista: {response_api.text}"

        #verdadera funcion

        listUnits = []
        speak_output = '  Lista: '
        data_array = response_api.json()
        for d in data_array:
            unit_id = d["id"]
            name = d["name"]
            unit_string = f"ID {unit_id} {name} "
            listUnits.append(unit_string)

        for l in listUnits:
            speak_output += l

        return (
            handler_input
            .response_builder
            .speak(speak_output)
            .ask('  Necesito que me digas la unidad deseada')
            .response
        )

class controller:
    def listMCID(handler_input, unit_id):
        #preguntar por id_user
        id_user = 1
        unit_id = unit_id

        url = f"{GENERAL_MANAGER}/units/{unit_id}/{id_user}"
        #response_api = requests.get(url)

        #falta obtencion de datos

        speak_output = f"  Listado de microcontenidos de unidad {unit_id} no funcional"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask('Dime la id del microcontenido')
                .response
        )

class getUnitIDIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("getUnitIDIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        unit_id = slots["unit_id"].value

        return controller.listMCID(handler_input, unit_id)

class listInformationMCIDIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("listInformationMCIDIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        micro_id = slots["micro_id"].value

        url = f"{GENERAL_MANAGER}/microcontent?id={micro_id}"
        response_api = requests.get(url)
        data_array = response_api.json()

        title = data_array["meta_data"]["title"]
        author = data_array["meta_data"]["author"]

        speak_output = f"  Información sobre microcontenido {micro_id}. Título {title} y su autor es {author}"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask('Reproduccion de lista de microcontenidos')
                .response
        )

class playMediaMCIDIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("playMediaMCIDIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        micro_id = slots["micro_id"].value

        url = f"{GENERAL_MANAGER}/microcontent?id={micro_id}"
        response_api = requests.get(url)
        data_array = response_api.json()

        for d in data_array["media"]:
            tipo = d["type"]
            url = d["url"]

        return (
            handler_input.responseBuilder
                .speak('Reproduciendo contenido')
                .addAudioPlayerPlayDirective(
                    'REPLACE_ALL',
                    url,
                    1,
                    0,
                    null
                )
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hola, dime tu nombre"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Chao!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "Fallo " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Hay un problema."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(persistence_adapter = s3_adapter)

#sb.add_request_handler(HasAuthLaunchRequestHandler())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(getNameIntentHandler())
sb.add_request_handler(listUnitIDIntentHandler())
sb.add_request_handler(getUnitIDIntentHandler())
sb.add_request_handler(listInformationMCIDIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
