import logging
import voluptuous as vol
import requests
import homeassistant.helpers.config_validation as cv
from homeassistant.components.notify import (
    ATTR_TARGET, ATTR_TITLE, PLATFORM_SCHEMA, BaseNotificationService)

CONF_URL = 'url'
CONFIG_NICKNAME = 'nickname'
CONFIG_TOKEN = 'token'
_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_URL): cv.string,
    vol.Required(CONFIG_NICKNAME): cv.string,
    vol.Optional(CONFIG_TOKEN): cv.string,
}, extra=vol.ALLOW_EXTRA)

def get_service(hass, config, discovery_info=None):
    """Get the custom notifier service."""
    url = config.get(CONF_URL)
    nickname = config.get(CONFIG_NICKNAME)
    token = config.get(CONFIG_TOKEN)
    return MatterNotificationService(url,nickname,token)

class MatterNotificationService(BaseNotificationService):
    def __init__(self, url, nickname, token=None):
        self._url = url
        self.nickname = nickname
        self.token = token
        
    def send_message(self, message="", **kwargs):
        title = kwargs.get(ATTR_TITLE)
        gateway = kwargs.get(ATTR_TARGET)
        
        data = {
            
            "text": "*" + title + "* \n" + message,
            "gateway": str(gateway[0]),
            "username": self.nickname
        }
        try:
            if self.token is None:
                response = requests.post(self._url, json=data)
            else:
                headers = {"Authorization": "Bearer " + self.token} 
                response = requests.post(self._url, json=data,headers = headers)
            _LOGGER.info("Message sent")
            response.raise_for_status()
        except requests.exceptions.RequestException as ex:
            _LOGGER.error("Error sending notification using matterbridge: %s", ex)