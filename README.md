# AppDaemon Smart-Home Thermostat Skill for Alexa
AppDaemon Smart-Home skill for Alexa delivering Home Assistant's **Climate entities as Thermostat endpoints**.</br>
This repository covers a couple of **AppDaemon** applications:
- *Module Name:* `ir_packets_control` *Class Name:* `HandleMqttACUnit'</br>
Handles the topics published by the MQTT HVAC component in Home Assistant,</br>
The application will send the correct IR Packet to the configured IR Blaster (preferably `Broadlink`).</br></br>
- *Module Name:* `ir_packets_control` *Class Name:* `TemperatureSensorToMqtt'</br>
Simple app for transforming state change events for a temperture sensor to mqtt messages for the climate entity, </br>
Seeing that most Air-Conditioner units doesn't come with a built-in temperature sensor, we'll have to add it on-top (of course it is not mandatory, you can tweak the code a bit to disable this function).</br></br>
- *Module Name:* `smarthome_custom_ac` *Class Name:* `AlexaCustomAC'</br>
This is the Smart-Home Skill backend. The class will register an API Endpoint in order to transform Home Assistant's MQTT HVAC component to Smart Thermostat Endpoints for Alexa.</br></br>

This repository also introduces a couple **AppDaemon** global modules which I use throug out my code:
- `ir_packets_manager` is a module used by the `ir_packats_control` module for holding the IR Packets.</br>
Please Note: inside this module is where you will add you own IR Packets if you'll need to.</br></br>
- `little_helpers` holds the helper functions.</br></br>
- `alexa_request` used by the `smarthome_custom_ac` module, holds the different directive request objects.</br></br>
- `alexa_response_erros` used by the `smarthome_custom_ac` module, holds the different error response objects.</br></br>
- `alexa_response_success` used by the `smarthome_custom_ac` module, holds the different success response objects.</br></br>

From Home Assistant point, AppDaemon is standing between the HVAC component and the Air Conditioner unit:</br>
`MQTT HVAC` publish mqtt messages >></br>
`AppDaemon` picks up these messages and communicates them to `Home Assistant` through it's REST API.
</br><br>

From Alexa's point, AppDaemon is standing between her and the Smart Thermostat Endpoint:</br>
`Alexa` will communicate to a designated `Lambda function` >></br>
The `Lambda function` will transfer the requests to `AppDaemon` and the responses back to `Alexa`>></br>
`AppDaemon` will again communicate to `Home Assistant` through it's REST API >></br>
`Home Assistant` will act according to the previous flow and publish the mqtt messages to `AppDaemon`.</br></br>

I hope the makes sense, if not, I'll try to edit so it'll perhaps be clearer.</br>
Anyways, I'm sure it'll make more sense as you go along with the guide.

## TOC
- [Prerequisites](#prerequisites)
  - [Known AC Units](#known-ac-units)
- [Configure Home Assistant](#configure-home-assistant)
- [Configure AppDaemon](#configure-appdaemon)
  - [Pre configure AppDaemon](#pre-configure-appdaemon)
  - [Place the modules](#place-the-modules)
  - [Add your own IR Packets](#add-your-own-ir-packets)
  - [Home Assistant to AppDaemon](#home-assistant-to-appdaemon)
  - [Alexa to AppDaemon](#alexa-to-appdaemon)
- [Configure Alexa Skill](#configure-alexa-skill)
  - [Prepare the lambda function for deployment](#prepare-the-lambda-function-for-deployment)
  - [Deploy the skill](#deploy-the-skill)
  - [Create account linking for the skill](#create-account-linking-for-the-skill)

## Prerequisites
- [Home Assistant](https://www.home-assistant.io/) accessible from the outside your network.
- [AppDaemon](https://appdaemon.readthedocs.io/en/latest/#) configured with both the [HASS](https://appdaemon.readthedocs.io/en/latest/CONFIGURE.html#configuration-of-the-hass-plugin) and the [MQTT](https://appdaemon.readthedocs.io/en/latest/CONFIGURE.html#configuration-of-the-mqtt-plugin) plugins.
- [MQTT Broker](http://mqtt.org/) I use [Mosquitto](https://mosquitto.org/)
- [IR Blaster](https://en.wikipedia.org/wiki/Infrared_blaster) preferably `Broadlink` connected to your Home Assistant environment.
- [Amazon Developer Account](https://developer.amazon.com/)
- [Amazon AWS Account](https://aws.amazon.com/)
- [ASK CLI](https://developer.amazon.com/docs/smapi/ask-cli-intro.html) configured and working. You can of course do it all via the various consoles, I prefer the cli. Follow [this](https://developer.amazon.com/docs/smapi/quick-start-alexa-skills-kit-command-line-interface.html) guide to familiarize yourself with `ask cli`.
- [OAuth 2.0 Auth-Code Infrastracture](https://oauth.net/2/) unless you host your own, you can just use Amazon's Security Profiles (it's built-in to the developer account anyway)
- Last but not least [Infra-Red controlled Air-Conditioner unit](https://en.wikipedia.org/wiki/Air_conditioning)

### Known AC Units
The following AC unit types are known and don't need any prior recording of the IR Packets,</br>
If you're using any of the following units, you just saved yourself a lot of time.</br>
If not... well, you'll have to aquire them before moving on with this guide.</br>
There severl approaches for aquring the IR Packets, you might even find them online, but if you won't and you're using broadlink, I recommend [NightRang3r's scripts](https://github.com/NightRang3r/Broadlink-e-control-db-dump).</br>
- **Electra Classic 35** type-name: `electra_classic_35`
- **Elco (I'm not what the actual model is, it's a small unit for the bedroom)** type-name: `elco_small`
If you do add your own packets (described later), please create a pull request commiting the updates, others might find it useful.

## Configure Home Assistant
This part is pretty basic, just add an entity of `mqtt` platform with the `climate` component, [MQTT HVAC](https://www.home-assistant.io/components/climate.mqtt/):</br>
- Please replace *<thermostat_name>* with the name of your ac unit (there are 5 recurrences).
- Please the `min_temp` and the `max_temp` with your own unit's limitations.
- Take note of the various mqtt topics, this is the way Home Assistant will communicate with AppDaemon.
- Restart your evnironment for the changes to take effect.
```yaml
climate:
  - platform: mqtt
    name: "<thermostat_name>"
    qos: 0
    retain: false
    send_if_off: false
    initial: 25
    current_temperature_topic: "tomerfi_thermostat/<thermostat_name>/current_temperature"
    mode_command_topic: "tomerfi_thermostat/<thermostat_name>/mode"
    modes:
      - "off"
      - "cool"
      - "heat"
    temperature_command_topic: "tomerfi_thermostat/<thermostat_name>/temperature"
    fan_mode_command_topic: "tomerfi_thermostat/<thermostat_name>/fan"
    fan_modes:
      - "auto"
      - "low"
      - "medium"
      - "high"
    min_temp: 17
    max_temp: 30
    temp_step: 1

```

## Configure AppDaemon
This section is better of splited to two sub-sections, the first one will cover the:</br>
`Home Assistant` >> `AppDaemon` >> `Home Assistant` >> `IR Blaster` flow.</br>
The second will cover the:</br>
`Alexa` >> `Lambda` >> `AppDaemon` >> `Home Assistant` >> `IR Blaster` flows.</br>

### Pre configure AppDaemon
Please configure both HASS and MQTT plugin for AppDaemon, here is the required configuration in `<appdaemon_path>/appdaemon.yaml`, please change the <> values with your own:
```yaml
appdaemon:
  threads: 10
  app_dir: <applications_path>
  api_port: <api_access_port>
  api_key: <api_password>
  plugins:
    HASS:
      namespace: default
      type: hass
      ha_url: <home_assistant_url>
      token: <long_lived_access_token>
    MQTT:
      namespace: mqtt
      type: mqtt
      verbose: false
      client_host: <mqtt_server_name_ip>
      client_port: <mqtt_server_name_port>
      client_id: <mqtt_server_client_id>
      client_user: <mqtt_server_user>
      client_password: <mqtt_server_password>
```

### Place the modules
Place the following modules from the repository in you `<appdaemon_path>/<apps_path>/`:
- [/appdaemon/apps/ir_packets_control](/appdaemon/apps/ir_packets_control.py)
- [/appdaemon/apps/ir_packets_manager](/appdaemon/apps/ir_packets_manager.py)
- [/appdaemon/apps/little_helpers](/appdaemon/apps/little_helpers.py)</br>
The following modules need to be added only if you plan to use the Alexa skill part of the project, if not you can just skip the following modules:
- [/appdaemon/apps/alexa_request](/appdaemon/apps/alexa_request.py)
- [/appdaemon/apps/alexa_response_error](/appdaemon/apps/alexa_response_error.py)
- [/appdaemon/apps/alexa_response_success](/appdaemon/apps/alexa_response_success.py)
- [//appdaemon/apps/smarthome_custom_ac](/appdaemon/apps/smarthome_custom_ac.py)


### Add your own IR Packets
`ir_packets_manager` is the module managing the IR Packets. It's a simple module with a:
- A function-per-unit-type that returns a long dictionary containing the IR Packets (ie: `get_ir_dict_electra_classic_35()`).</br>
If you'll need to add your own IR Packets, you'll need to create a new function exactly like the two existing ones.
- A simple dictionary the translates the ac type name to the correct function (`ac_type_to_packet_func`).</br>
If you'll need to add you own AC Type, you'll need to add a `key-value` to this dict, containing the your new type name as key and the new function as value.
- A function you don't need to worry about is `get_ac_packet(ac_type, mode, speed = None, temp = None)`, it's used internally to access the module.</br>
You can see the full file [here](appdaemon/apps/ir_packets_manager.py).<br>

Here's a template for you IR Packets function, add your packets inside the quotation marks for the corresponding `mode/fan/temp_x` key (note that this example is for a unit that supports 18-30 degrees temperature, you can add/subtract keys according to your unit type, just make sure to configure the same for the Home Assistant's component):
```python
def get_ir_dict_your_ac_type():
  return {
    "off": "",
    "cool" : {
      "low" : {
        "temp_18": "",
        "temp_19": "",
        "temp_20": "",
        "temp_21": "",
        "temp_22": "",
        "temp_23": "",
        "temp_24": "",
        "temp_25": "",
        "temp_26": "",
        "temp_27": "",
        "temp_28": "",
        "temp_29": "",
        "temp_30": ""
      },
      "medium" : {
        "temp_18": "",
        "temp_19": "",
        "temp_20": "",
        "temp_21": "",
        "temp_22": "",
        "temp_23": "",
        "temp_24": "",
        "temp_25": "",
        "temp_26": "",
        "temp_27": "",
        "temp_28": "",
        "temp_29": "",
        "temp_30": ""
      },
      "high" : {
        "temp_18": "",
        "temp_19": "",
        "temp_20": "",
        "temp_21": "",
        "temp_22": "",
        "temp_23": "",
        "temp_24": "",
        "temp_25": "",
        "temp_26": "",
        "temp_27": "",
        "temp_28": "",
        "temp_29": "",
        "temp_30": ""
      },
      "auto" : {
        "temp_18": "",
        "temp_19": "",
        "temp_20": "",
        "temp_21": "",
        "temp_22": "",
        "temp_23": "",
        "temp_24": "",
        "temp_25": "",
        "temp_26": "",
        "temp_27": "",
        "temp_28": "",
        "temp_29": "",
        "temp_30": ""
      }
    },
    "heat": {
      "low" : {
        "temp_18": "",
        "temp_19": "",
        "temp_20": "",
        "temp_21": "",
        "temp_22": "",
        "temp_23": "",
        "temp_24": "",
        "temp_25": "",
        "temp_26": "",
        "temp_27": "",
        "temp_28": "",
        "temp_29": "",
        "temp_30": ""
      },
      "medium" : {
        "temp_18": "",
        "temp_19": "",
        "temp_20": "",
        "temp_21": "",
        "temp_22": "",
        "temp_23": "",
        "temp_24": "",
        "temp_25": "",
        "temp_26": "",
        "temp_27": "",
        "temp_28": "",
        "temp_29": "",
        "temp_30": ""
      },
      "high" : {
        "temp_18": "",
        "temp_19": "",
        "temp_20": "",
        "temp_21": "",
        "temp_22": "",
        "temp_23": "",
        "temp_24": "",
        "temp_25": "",
        "temp_26": "",
        "temp_27": "",
        "temp_28": "",
        "temp_29": "",
        "temp_30": ""
      },
      "auto" : {
        "temp_18": "",
        "temp_19": "",
        "temp_20": "",
        "temp_21": "",
        "temp_22": "",
        "temp_23": "",
        "temp_24": "",
        "temp_25": "",
        "temp_26": "",
        "temp_27": "",
        "temp_28": "",
        "temp_29": "",
        "temp_30": ""
      }
    }
  }
```
Here is a template for the updated dictionary binding type name to function, the key is the type we use to configure the application, the value is the funcion you just created abobe this paragraph.
```python
ac_type_to_packet_func = {
  "elco_small": get_ir_dict_elco_small,
  "electra_classic_35": get_ir_dict_electra_classic_35,
  "your_ac_type_name": get_ir_dict_your_ac_type
}
```

### Home Assistant to AppDaemon
After configuring Home Assistant's entity and gathering our IR Packets into the `ir_packets_manager` module, we have an entity that publishes mqtt messages based on its activity, we now need to make AppDaemon catch these messages and instruct Home Assistant's API on what to do next with the correct IR Packet.</br></br>

First, let's configure our applications in `<appdaemon_path>/<apps_path>/apps.yaml>`:
- Please change `<thermostat_name>` with your unit's name
- For `climate_entity` update the entity name you've created in the Home Assistant configuration section.
- For `ir_send_service` update the name of you IR Blaster service. Please Note, if you're not using `Broadlink`, you should know that the application will send the IR Packet to the service as json with the `packet` key.
- The `<thermostat_name>_control` application:
  - For `ac_type` update the type of you unit based on the previous section for aquiring the IR Packets.
  - For `default_mode_for_on` set the default mode of your unit, options are:
    - `heat`
    - `cool`
  - For `mode_command_topic` update the topic from you climate component's `mode_command_topic` key.
  - For `temperature_command_topic` update the topic from you climate component's `temperature_command_topic` key.
  - For `fan_mode_command_topic` update the topic from you climate component's `fan_mode_command_topic` key.
- The `temperature_sensor_to_mqtt` application:
  - For `sensor_entity` update with the full entity name of the sensor which holds the current temperature as its state.
  - For `topic` update the topic from you climate component's `current_temperature_topic` key.
  - The optional arguments `mode_entity_for_update`,`temperature_entity_for_update`and `fan_mode_entity_for_update`, are optional and used to change the state of any helpers you use for controlling the climate in order to keep your helpers in-sync with alexa's commands to the climate. Please Note, the state is change internally, no action will be taken by Home Assistant based on the state changed according to these option arguments.
```yaml
global_modules:
  - ir_packets_manager
  - little_helpers
  - alexa_request #(ignore this if you don't plan on using Alexa)
  - alexa_response_error #(ignore this if you don't plan on using Alexa)
  - alexa_response_success #(ignore this if you don't plan on using Alexa)

<thermostat_name>_control:
  module: ir_packets_control
  class: HandleMqttACUnit
  climate_entity: climate.entity_id
  ir_send_service: switch.broadlink_send_packet_X
  ac_type: "elco_small"
  default_mode_for_on: "heat"
  mode_command_topic: "tomerfi_thermostat/<thermostat_name>/mode"
  temperature_command_topic: "tomerfi_thermostat/<thermostat_name>/temperature"
  fan_mode_command_topic: "tomerfi_thermostat/<thermostat_name>/fan"
  # the following are optional and in use only if you have any helper entities you need to keep in-sync with alexa's commands
  mode_entity_for_update: input_select.input_select_controlling_operation_mode
  temperature_entity_for_update: input_number.input_select_controlling_temperature_select 
  fan_mode_entity_for_update: input_select.input_select_controlling_fan_level
  
temperature_sensor_to_mqtt:
  module: ir_packets_control
  class: TemperatureSensorToMqtt
  sensor_entity: sensor.nursery_broadlink_a1_temperature
  topic: "tomerfi_thermostat/<thermostat_name>/current_temperature"
```

Restart your system and if everything was configured correctly, you can now use the `climate entity` in `Home Assistnat` and `AppDaemon` will handle the rest.</br></br>

If everything is working, please continue to the next section and configure Alexa's skill.</br>

### Alexa to AppDaemon
If you reached this part, you now have a fully working `climate component` controlling your ac unit. Now we want to spice it up with some and create an `API Endpoint` that will respond to Alexa's requests.</br>
Add the following application configuration to your `<appdaemon_path>/<apps_path>/apps.yaml`:
- For `entities` replace with you entity id from the Home Assistant's configuration section (multiple unit supported).
- For `default_mode_for_on` set the default mode of your unit, options are:
  - `heat`
  - `cool`
- For `scale` choose your scale in use, option are:
  - `CELSIUS`
  - `FAHRENHEIT`
  - `KELVIN`
```yaml
smarthome_custom_ac:
  module: smarthome_custom_ac
  class: AlexaCustomAC
  entities:
    - climate.entity_id
  default_mode_for_on: "heat"
  scale: "CELSIUS"
  global_dependencies:
    - alexa_requests
    - alexa_response_error
    - alexa_response_success
    - little_helpers
```
That's it, you now have a working Smart-Home Alexa skill backend, ready to respond to request sent to:</br>
https://<your_ha_ip_or_name>/api/appdaemon/AlexaCustomAC</br>

Jump over to the next section for configuring your Alexa skill.

## Configure Alexa Skill
The skill is actually ready, you just need to configure it and deploy it to `Alexa` and `Lambda` servers.</br>
The `alexa` folder in the repository is the skill to be deployed:
- `.ask` holds the configuration for the `ask cli` end with details for the deployment.
- `.venv` is a python3 virtual environment created by the `post_new_hook_sh` script, detailed next.
- `hooks/post_new_hook.sh` is the script executed by the `ask cli` right after a `ask new` command is issued, it's job is to create a python venv and install all the packages described in `requirements.txt` in order to make sure everything is going to work ok.</br>
There's no need for you to use `ask new` in this project, the skill is already created, that's why the `.venv` folder is included.
- `hooks/pre_deploy_hook.sh` is the script executed by the `ask cli` for before the deployment based on the `ask deploy` command, its job it to create a folder and prepare it with all the code and the modules to be uploaded to lambda.
- `lambda/lambda_func.py` is the lambda function for the skill, it will recieve requests from Alexa's servers and forward them to our new `AppDaemon` API Endpoint, and of course transfer our `AppDaemon` responses back to Alexa's servers.</br>
**THIS IS THE ONLY FILE YOU NEED TO EDIT BEFORE DEPLOYMENT**
- `lambda/requirements.txt` is the python requirements file for the lambda required python modules.
- `skill.json` is the skill configuration file.</br></br>

### Prepare the lambda function for deployment
Open the file `/alexa/lambda/lambda_func.py`, updated your Home Assistant/AppDaemon url, save the the file and that's it. You're ready for deployment.</br>
Please Note, as for AppDaemon 3.0.2 version, Legacy Password is requierd.</br>
In future version, I think Andrew plans on implenting the Long-Lived Access Tokens methodology from Home Assistant, if so I'll update this repository accordingly, so please follow it for any future adjustments.</br>
The text to be edited by you is, of course lose the less-then and greater-then characters:
```text
api_url = "https://<your_ha_fqdn_and port>/api/appdaemon/AlexaCustomAC?api_password=<appdaemon_api_password>"
```

### Deploy the skill
Place yourself in the same path as the `.ask` folder, (which is inside the `alexa` folder if you preserved the order of this repository) and type the following command:
```shell
ask deploy
```
That's it, your skill is deployed to both `Alexa` and `Lambda` servers.

### Create account linking for the skill
For this stage, please prepare all of your chosen OAuth 2.0 service details.</br>
If you don't have a OAuth 2.0 infrastructure at your disposal, I recommend using [Amazon's Security Profile](https://developer.amazon.com/docs/alexa-voice-service/activate-security-profile.html) it's very simple and quick.</br>
The redirect url for the configuration will be: *https://pitangui.amazon.com/api/skill/link/M70Y38N3PTU2A*.</br></br>

After deploying your skill, you can now check the configuration file `.ask/config`, you'll notice it's been updated with the details of your project.</br>
Grab the skill id from the config file and run the following command:
```shell
ask api create-account-linking -s <your_skill_id>
```
This command will walk you through the proccess of configuring you account linking, configure it as follows:
- **Authorization URL** type your OAuth authorization url, add the `redirect_url`. If you're using Amazon's Security Profiles the value is: *https://www.amazon.com/ap/oa/?redirect_url=https://pitangui.amazon.com/api/skill/link/M70Y38N3PTU2A*
- **Client ID** you OAuth client id.
- **Scopes** type `profile`
- **Domains** leave blank or default
- **Authorization Grant Type** choose `AUTH_CODE`
- **Access Token URL** type your OAuth access token url. If you're using Amazon's Security Profiles, the value is: *https://api.amazon.com/auth/o2/token*
- **Client Secret** type your OAuth client secret.
- **Client Authentication Scheme** choose `REQUEST_BODY_CREDENTIALS`

Please Note, the `ask api <subcommand>` tool is a direct access api to your skills, which means there's no need to re-deploy after using the `ask api` tool, everything you do is done directly to your skills.
