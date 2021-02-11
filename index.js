/* *
 * Microlearning
 * */
const Alexa = require('ask-sdk-core');
const persistenceAdapter = require('ask-sdk-s3-persistence-adapter');


/*
 * Values auth
 */

var name, surname, day, year, month, id_device;


const LaunchRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
    },
    handle(handlerInput) {
        const speakOutput = 'Bienvenido a Microlearning.';

        const repromptText = 'Necesito que me cuentes tu nombre y tu apellido.'
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt(repromptText)
            .getResponse();
    }
};

const HasAuthLaunchRequestHandler = {
    canHandle(handlerInput) {

        const attributesManager = handlerInput.attributesManager;
        const sessionAttributes = attributesManager.getSessionAttributes() || {};

        name = sessionAttributes.hasOwnProperty('name') ? sessionAttributes.name : undefined;
        surname = sessionAttributes.hasOwnProperty('surname') ? sessionAttributes.surname : undefined;

        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest'
            && name && surname;
    },
    handle(handlerInput) {
        const attributesManager = handlerInput.attributesManager;
        const sessionAttributes = attributesManager.getSessionAttributes() || {};

        const name = sessionAttributes.hasOwnProperty('name') ? sessionAttributes.name : undefined;
        const surname = sessionAttributes.hasOwnProperty('surname') ? sessionAttributes.surname : undefined;

        const speakOutput = `Bienvenido de nuevo, ${name} ${surname}`;

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};

const getNameIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'getNameIntent';
    },
    async handle(handlerInput) {

        name = handlerInput.requestEnvelope.request.intent.slots.name.value;
        surname = handlerInput.requestEnvelope.request.intent.slots.surname.value;
        id_device = Alexa.getDeviceId(handlerInput.requestEnvelope);

        //guardamos datos
        const attributesManager = handlerInput.attributesManager;

        const nameAttributes = {
            "name": name,
            "surname": surname,
            "id_device": id_device
        };

        attributesManager.setPersistentAttributes(nameAttributes);
        await attributesManager.savePersistentAttributes();

        const speakOutput = `Muchas gracias, ${name} ${surname} con ${id_device}. Ahora me tendrás que decir tu cumpleaños.`;

        //envio de datos a la api

        return handlerInput.responseBuilder
            .speak(speakOutput)
            //.reprompt('add a reprompt if you want to keep the session open for the user to respond')
            .getResponse();
    }
};

const getBirthdayIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === "IntentRequest"
            && Alexa.getIntentName(handlerInput.requestEnvelope) === "getBirthdayIntent";
    },
    async handle(handlerInput) {

        day = handlerInput.requestEnvelope.request.intent.slots.day.value;
        month = handlerInput.requestEnvelope.request.intent.slots.month.value;
        year = handlerInput.requestEnvelope.request.intent.slots.year.value;

        //guardamos datos
        const attributesManager = handlerInput.attributesManager;

        const birthdayAttributes = {
            "year": year,
            "month": month,
            "day": day
        };

        attributesManager.setPersistentAttributes(birthdayAttributes);
        await attributesManager.savePersistentAttributes();

        const speakOutput = `Gracias. Tu cumple es ${month} ${day} ${year}. Procedemos a autentificarte.`;

        //envio de datos a la api

        return handlerInput.responseBuilder
            .speak(speakOutput)
            //.reprompt('hola')
            .getResponse();
    }
};

const getUnitIDIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === "IntentRequest"
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'getUnitIDIntent';
    },
    handle(handlerInput) {
        //despues de la lectura de unidades

        const unit_id = handlerInput.requestEnvelope.request.intent.slots.unit_id.value;

        const speakOutput = `Has seleccionado la unidad número ${unit_id}`;

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};

const getMCIDIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'getMCIDIntent';
    },
    handle(handlerInput) {
        //despues de la lectura de microcontenidos

        const micro_id = handlerInput.requestEnvelope.request.intent.slots.micro_id.value;

        const speakOutput = `Has seleccionado el contenido número ${micro_id}`;

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
}

const HelpIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.HelpIntent';
    },
    handle(handlerInput) {
        const speakOutput = 'You can say hello to me! How can I help?';

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt(speakOutput)
            .getResponse();
    }
};

const CancelAndStopIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.CancelIntent'
                || Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.StopIntent');
    },
    handle(handlerInput) {
        const speakOutput = 'Goodbye!';

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};
/* *
 * FallbackIntent triggers when a customer says something that doesn’t map to any intents in your skill
 * It must also be defined in the language model (if the locale supports it)
 * This handler can be safely added but will be ingnored in locales that do not support it yet
 * */
const FallbackIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.FallbackIntent';
    },
    handle(handlerInput) {
        const speakOutput = 'Sorry, I don\'t know about that. Please try again.';

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt(speakOutput)
            .getResponse();
    }
};
/* *
 * SessionEndedRequest notifies that a session was ended. This handler will be triggered when a currently open
 * session is closed for one of the following reasons: 1) The user says "exit" or "quit". 2) The user does not
 * respond or says something that does not match an intent defined in your voice model. 3) An error occurs
 * */
const SessionEndedRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'SessionEndedRequest';
    },
    handle(handlerInput) {
        console.log(`~~~~ Session ended: ${JSON.stringify(handlerInput.requestEnvelope)}`);
        // Any cleanup logic goes here.
        return handlerInput.responseBuilder.getResponse(); // notice we send an empty response
    }
};
/* *
 * The intent reflector is used for interaction model testing and debugging.
 * It will simply repeat the intent the user said. You can create custom handlers for your intents
 * by defining them above, then also adding them to the request handler chain below
 * */
const IntentReflectorHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest';
    },
    handle(handlerInput) {
        const intentName = Alexa.getIntentName(handlerInput.requestEnvelope);
        const speakOutput = `You just triggered ${intentName}`;

        return handlerInput.responseBuilder
            .speak(speakOutput)
            //.reprompt('add a reprompt if you want to keep the session open for the user to respond')
            .getResponse();
    }
};
/**
 * Generic error handling to capture any syntax or routing errors. If you receive an error
 * stating the request handler chain is not found, you have not implemented a handler for
 * the intent being invoked or included it in the skill builder below
 * */
const ErrorHandler = {
    canHandle() {
        return true;
    },
    handle(handlerInput, error) {
        const speakOutput = 'Sorry, I had trouble doing what you asked. Please try again.';
        console.log(`~~~~ Error handled: ${JSON.stringify(error)}`);

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt(speakOutput)
            .getResponse();
    }
};

const LoadAuthInterceptor = {
    async process(handlerInput) {
        const attributesManager = handlerInput.attributesManager;
        const sessionAttributes = await attributesManager.getPersistenAttributes() || {};

        name = sessionAttributes.hasOwnProperty('name') ? sessionAttributes.name : undefined;
        surname = sessionAttributes.hasOwnProperty('surname') ? sessionAttributes.surname : undefined;

        if(name && surname) {
            attributesManager.setSessionAttributes(sessionAttributes);
        }
    }
}

/**
 * This handler acts as the entry point for your skill, routing all request and response
 * payloads to the handlers above. Make sure any new handlers or interceptors you've
 * defined are included below. The order matters - they're processed top to bottom
 * */
exports.handler = Alexa.SkillBuilders.custom()
    .withPersistenceAdapter(
        new persistenceAdapter.S3PersistenceAdapter({bucketName:process.env.S3_PERSISTENCE_BUCKET})
    )
    .addRequestHandlers(
        LaunchRequestHandler,
        //HasAuthLaunchRequestHandler,
        getNameIntentHandler,
        getBirthdayIntentHandler,
        HelpIntentHandler,
        CancelAndStopIntentHandler,
        FallbackIntentHandler,
        SessionEndedRequestHandler,
        IntentReflectorHandler)
    .addErrorHandlers(
        ErrorHandler)
    .addRequestInterceptors(
        LoadAuthInterceptor
    )
    .lambda();
