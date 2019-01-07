import json
import logging
import requests

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.ERROR)

def lambda_handler(request, context):
    response = None
    try:
        _LOGGER.debug("Directive:")
        _LOGGER.debug(json.dumps(request, indent=4, sort_keys=True))

        api_url = "https://<your_ha_fqdn_and port>/api/appdaemon/AlexaCustomAC?api_password=<appdaemon_api_password>"
        api_headers = {
            "Content-Type": "application/json"
            }

        response = requests.post(url=api_url, data=json.dumps(request, indent=4, sort_keys=True), headers=api_headers, verify=True)

    except Exception as ex:
        _LOGGER.error(ex)
        raise
    finally:
        if response is not None:
            _LOGGER.debug("Response:")
            _LOGGER.debug(json.loads(response.content))
            return json.loads(response.content)
        else:
            _LOGGER.error("No Response")
            return None


