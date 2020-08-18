const openwhisk = require('openwhisk');
const ow = openwhisk();

function main(params) {

    switch(params.action) {

        case 'identify_user':

            return ow.actions.invoke({
                name: 'watson-assistant/identify_user',
                blocking: true,
                result: true,
                params: params.args
            })
            .then((result) => {
                return result;
            });

        case 'get_user_forms':

            return ow.actions.invoke({
                name: 'watson-assistant/get_user_forms',
                blocking: true,
                result: true,
                params: params.args
            })
            .then((result) => {
                return result;
            });
        case 'load_form':
            return ow.actions.invoke({
                name: 'watson-assistant/get_questionnaire',
                blocking: true,
                result: true,
                params: params
            })
            .then((result) => {
                return ow.actions.invoke({
                    name: 'watson-assistant/flatten_form',
                    blocking: true,
                    result: true,
                    params: result
                });
            }).then((result) => {
                return ow.actions.invoke({
                    name: 'watson-assistant/create_dialog',
                    blocking: true,
                    result: true,
                    params: result
                })
            });

        default:
            console.log("Action " + params.action + " not recognized.");
    }
}
