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

def check_credentials(id_device):
    #check user
    
    url = f"{GENERAL_MANAGER}/check_user/alexa/{id_device}"
    response_api = requests.get(url)
    
    if response_api.status_code == 200:
        return True
    else:
        return False
    
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
        #obtener id_device
        sys_object = handler_input.request_envelope.context.system
        id_device = sys_object.device.device_id
        
        #comprobacion credenciales
        if (not check_credentials(id_device)):
            return(
                handler_input
                .response_builder
                .speak('Usuario no identificado')
                .response
            )
        
        url = GENERAL_MANAGER + '/get_units'
        response_api = requests.get(url)
        
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
        
        #obtener id_device
        sys_object = handler_input.request_envelope.context.system
        id_device = sys_object.device.device_id
        
        #comprobacion credenciales
        if (not check_credentials(id_device)):
            return(
                handler_input
                .response_builder
                .speak('Usuario no identificado')
                .response
            )
        
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

'''
CLASES RELACIONADAS CON LA REPRODUCCION DE VIDEO/AUDIO SOBRE microcontenidos
'''
#REPRODUCCION A TRAVES DE URL (NO FUNCIONAL, POR AHORA)
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

#REPRODUCCION DE VIDEO A TRAVES DE FICHERO .JSON
class IntentAPLtHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("intentAPLtest")(handler_input) and
                handler_input.request_envelope.request.object_type != "Alexa.Presentation.APL.UserEvent"

    def handle(self, handler_input):
        # type: (HandlerInput) ->  Response
        # Check if is the apl interface is sopported

        persistent_attr = handler_input.attributes_manager.persistent_attributes
        if handler_input.request_envelope.context.system.device.supported_interfaces.alexa_presentation_apl:
            render_document_directive = apl.render_document_directive.RenderDocumentDirective("token_video", j_apl_tv)
            handler_input.attributes_manager.persistent_attributes["media_type"] = "video"
            handler_input.attributes_manager.persistent_attributes["media_state"] = "playing"
            handler_input.attributes_manager.save_persistent_attributes()
            handler_input.attributes_manager.session_attributes["state"] = "VIDEO_PLAYING"
            handler_input.response_builder.add_directive(render_document_directive)

        else:
            speak_output = "Este dispositivo no soporta A.P.L."
            handler_input.response_builder.speak(speak_output).ask(" ")

        return handler_input.response_builder.response

class MediaControlIntentHandler(AbstractRequestHandler):
    """ Handler para el intent SeekIntent, usado para proporcionar control temporal en la reproduccion del video"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("MediaControlIntent")(handler_input) and
                handler_input.attributes_manager.persistent_attributes["media_state"] == "playing")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        media_type = handler_input.attributes_manager.persistent_attributes.get("media_type")

        """---- Extraccion de datos ----"""
        # Extacion de la id de los valores de los slots
        intent = handler_input.request_envelope.request.intent
        action = intent.slots["action"].resolutions.resolutions_per_authority[0].values[0].value.id
        time = intent.slots["time"].resolutions.resolutions_per_authority[0].values[0].value.id
        value = intent.slots["number"].value

        """ --- Cálculo de los tiempos de reproducción pedidos ----
        """
        offset = 0
        multiplier_dic = {'sec': 1000, 'min': 60000, 'hour': 3600000}
        multiplier = multiplier_dic.get(time, 0)
        if action == "back":
            offset = - int(value) * multiplier
        else:
            offset = int(value) * multiplier

        """---- Creacion de comandos y Directiva de video ----"""
        if media_type == "video":
            # Comando rewind, necesario para reiniciar la posicion actual de reproduccion a 0.
            apl_rewind = apl.ControlMediaCommand(command="rewind", component_id="videoPlayer")
            # Comando seek, value contiene el tiempo de reproduccion al que se quiere saltar (en milisegundos)
            apl_seek = apl.ControlMediaCommand(command="seek", component_id="videoPlayer", value=offset)
            # Comando play, inicia la reproduccion del video (necesario despues del comando seek)
            apl_play = apl.ControlMediaCommand(command="play", component_id="videoPlayer")

            # Directiva ExecuteCommands
            if action == "go_to":
                apl_ecd = apl.execute_commands_directive.ExecuteCommandsDirective([apl_rewind, apl_seek, apl_play],
                                                                                  "token_video")
            else:
                apl_ecd = apl.execute_commands_directive.ExecuteCommandsDirective([apl_seek, apl_play], "token_video")

            return handler_input.response_builder.add_directive(apl_ecd).response
        elif media_type == "audio":
            attr_persistent = handler_input.attributes_manager.persistent_attributes
            mic = MicroContent(attr_persistent["microcontent"])
            previous_offset = attr_persistent["media_cursor"]
            current_offset = previous_offset + offset
            audio_stream = audioplayer.stream.Stream(url=mic.getvideos()[0].getvideourl(), token="audio_token",
                                                     offset_in_milliseconds=current_offset)
            audio_item = audioplayer.audio_item.AudioItem(stream=audio_stream)
            play_behavior = interfaces.audioplayer.PlayBehavior.REPLACE_ALL
            api_directive = interfaces.audioplayer.PlayDirective(play_behavior, audio_item)
            handler_input.response_builder.add_directive(api_directive)
            return handler_input.response_builder.response

#REPRODUCCION DE AUDIO A TRAVES DE FICHERO .JSON
class AudioTestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("audiotestintent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) ->  Response
        # Check if is the apl interface is sopported
        handler_input.attributes_manager.session_attributes["state"] = "AUDIO_PLAYING"
        handler_input.attributes_manager.persistent_attributes["media_type"] = "audio"
        handler_input.attributes_manager.persistent_attributes["media_state"] = "playing"
        handler_input.attributes_manager.save_persistent_attributes()
        if handler_input.request_envelope.context.system.device.supported_interfaces.audio_player:
            attr_persistent = handler_input.attributes_manager.persistent_attributes
            mic = MicroContent(attr_persistent["microcontent"])
            audio_stream = audioplayer.stream.Stream(url=mic.getvideos()[0].getvideourl(), token="audio_token")
            audio_item = audioplayer.audio_item.AudioItem(stream=audio_stream)
            play_behavior = audioplayer.play_behavior.PlayBehavior.REPLACE_ALL
            ap_directive = audioplayer.play_directive.PlayDirective(play_behavior, audio_item)
            handler_input.response_builder.add_directive(ap_directive)

        else:
            speak_output = "Este dispositivo no tienes soporte para la interfaz audioPlayer"
            handler_input.response_builder.speak(speak_output).ask("")

        return handler_input.response_builder.response


class AudiofinishedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):  # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("AudioPlayer.PlaybackFinished")(handler_input)

    def handle(self, handler_input):  # type: (HandlerInput) -> Response
        return handler_input.response_builder.speak("fin de reproduccion").response


class AudioStopHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_request_type("AudioPlayer.PlaybackStopped")(handler_input) or
                ask_utils.is_request_type("AudioPlayer.PlaybackFinished")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr_persistent = handler_input.attributes_manager.persistent_attributes
        attr_persistent["media_cursor"] = handler_input.request_envelope.request.offset_in_milliseconds
        handler_input.attributes_manager.save_persistent_attributes()
        return handler_input.response_builder.response
        

'''
AYUDA, CONTROL DE LA skill
'''
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
