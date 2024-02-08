"""Define a base client for interacting with Bradford White Connect."""

import json
import logging
from typing import Dict, Optional

import aiohttp
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from .constants import (
    BRADFORD_WHITE_APP_ID,
    BRADFORD_WHITE_APP_SECRET,
    BradfordWhiteConnectHeatingModes,
)
from .exceptions import (
    BradfordWhiteConnectAuthenticationError,
    BradfordWhiteConnectUnknownException,
)
from .types import Device, Property, PropertyWrapper

logger = logging.getLogger(__name__)


class BradfordWhiteConnectClient:
    token: Optional[str] = None

    def __init__(
        self,
        email: str,
        password: str,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        self.email = email
        self.password = password

        if session is None:
            self.session = aiohttp.ClientSession()
        else:
            self.session = session

    @retry(
        retry=retry_if_exception_type(BradfordWhiteConnectUnknownException),
        reraise=True,
        wait=wait_fixed(10),
        stop=stop_after_attempt(6),
        before_sleep=before_sleep_log(logger, logging.DEBUG),
    )
    async def http_get_request(self, uri: str, headers: Dict[str, str]) -> str:
        """
        Sends an HTTP GET request to the specified URI with the given headers.

        Args:
            uri (str): The URI to send the request to.
            headers (Dict[str, str]): The headers to include in the request.

        Returns:
            str: The response text from the server.

        Raises:
            HTTPError: If the response status code is not in the 200-299 range.
        """
        async with self.session.get(uri, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def http_post_request(self, uri, headers, data):
        """
        Sends an HTTP POST request.

        Args:
            uri (str): The URI to send the request to.
            headers (dict): The headers to include in the request.
            data (bytes): The data to include in the request body.

        Returns:
            The response object from the server.
        """
        # trunk-ignore(flake8/E501)
        async with self.session.post(uri, headers=headers, data=data) as response:
            response.raise_for_status()
            return await response.json()

    async def get_devices(self):
        headers = {
            "Host": "ads-field.aylanetworks.com",
            "accept": "*/*",
            "user-agent": "BWConnect/1.2.1 (iPhone; iOS 17.3; Scale/3.00)",
            "accept-language": "en;q=1, am-US;q=0.9",
            "authorization": f"auth_token {self.token}",
        }

        url = "https://ads-field.aylanetworks.com" "/apiv1/devices.json"
        responseJson = await self.http_get_request(url, headers=headers)

        # Map to Device class
        return [Device(**item["device"]) for item in responseJson]

    async def get_device_properties(self, device: Device):
        headers = {
            "Host": "ads-field.aylanetworks.com",
            "accept": "*/*",
            "user-agent": "BWConnect/1.2.1 (iPhone; iOS 17.3; Scale/3.00)",
            "accept-language": "en;q=1, am-US;q=0.9",
            "authorization": f"auth_token {self.token}",
        }

        url = (
            f"https://ads-field.aylanetworks.com"
            f"/apiv1/dsns/{device.dsn}/properties.json"
        )
        responseJson = await self.http_get_request(url, headers=headers)

        # Map to PropertyWrapper class
        # trunk-ignore(flake8/E501)
        return [PropertyWrapper(Property(**item["property"])) for item in responseJson]

    async def set_device_heat_mode(
        self, device, mode: BradfordWhiteConnectHeatingModes
    ):
        headers = {
            "Host": "ads-field.aylanetworks.com",
            "accept": "*/*",
            "content-type": "application/json",
            "x-ayla-source": "Mobile",
            "accept-language": "en;q=1, am-US;q=0.9",
            "authorization": f"auth_token {self.token}",
            "user-agent": "BWConnect/1.2.1 (iPhone; iOS 17.3; Scale/3.00)",
        }

        data = {"datapoint": {"value": mode}}

        url = (
            f"https://ads-field.aylanetworks.com"
            f"/apiv1/dsns/{device.dsn}/properties/"
            f"set_heat_mode_{mode}/datapoints.json"
        )

        return await self.http_post_request(
            url,
            headers=headers,
            data=json.dumps(data),
        )

    async def update_device_set_point(self, device, value):
        headers = {
            "Host": "ads-field.aylanetworks.com",
            "accept": "*/*",
            "content-type": "application/json",
            "x-ayla-source": "Mobile",
            "accept-language": "en;q=1, am-US;q=0.9",
            "authorization": f"auth_token {self.token}",
            "user-agent": "BWConnect/1.2.1 (iPhone; iOS 17.3; Scale/3.00)",
        }

        data = {"datapoint": {"value": value}}

        url = (
            f"https://ads-field.aylanetworks.com"
            f"/apiv1/dsns/{device.dsn}/properties/"
            f"water_setpoint_in/datapoints.json"
        )

        await self.http_post_request(
            url,
            headers=headers,
            data=json.dumps(data),
        )

    async def authenticate(self):
        """
        Authenticates the client with the server.

        Raises:
            AuthenticationError: If authentication fails.

        Returns:
            None
        """

        headers = {
            "Host": "user-field.aylanetworks.com",
            "accept": "*/*",
            "content-type": "application/json",
            "user-agent": "BWConnect/1.2.1 (iPhone; iOS 17.3; Scale/3.00)",
            "accept-language": "en;q=1, am-US;q=0.9",
        }

        data = {
            "user": {
                "email": self.email,
                "application": {
                    "app_id": BRADFORD_WHITE_APP_ID,
                    "app_secret": BRADFORD_WHITE_APP_SECRET,
                },
                "password": self.password,
            }
        }

        responseJson = await self.http_post_request(
            "https://user-field.aylanetworks.com/users/sign_in.json",
            data=json.dumps(data),
            headers=headers,
        )

        if responseJson.get("access_token") is None:
            raise BradfordWhiteConnectAuthenticationError("Auth failed")

        self.token = responseJson["access_token"]
