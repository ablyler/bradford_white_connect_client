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
    async def http_get_request(
        self,
        uri: str,
        headers: Dict[str, str],
        retrying_after_login: bool = False,
    ) -> str:
        """
        Sends an HTTP GET request to the specified URI with the given headers.

        Args:
            uri (str): The URI to send the GET request to.
            headers (Dict[str, str]): The headers to include in the request.
            retrying_after_login (bool, optional): Indicates whether the
            request is being retried after logging in. Defaults to False.

        Returns:
            str: The response body as a string.

        Raises:
            BradfordWhiteConnectUnknownException: If a 401 status code is
            received after logging in. requests.exceptions.HTTPError: If a
            non-2xx status code is received.
        """
        async with self.session.get(uri, headers=headers) as response:
            # catch access denied errors and attempt to re-authenticate
            if response.status == 401:
                # if retrying after login, raise exception
                if retrying_after_login:
                    raise BradfordWhiteConnectUnknownException(
                        "Received status code 401 after logging in"
                    )

                # update headers with new token
                logger.debug("Token may be expired - retrying login")
                await self.authenticate()
                headers["authorization"] = f"auth_token {self.token}"

                # retry the request
                return await self.http_get_request(
                    uri, headers, retrying_after_login=True
                )

            response.raise_for_status()
            return await response.json()

    async def http_post_request(
        self, uri, headers, data, retrying_after_login: bool = False
    ):
        """
        Sends an HTTP POST request to the specified URI.

        Args:
            uri (str): The URI to send the request to.
            headers (dict): The headers to include in the request.
            data (dict): The data to include in the request body.
            retrying_after_login (bool, optional): Indicates whether
            the request is being retried after logging in. Defaults to False.

        Returns:
            dict: The JSON response from the server.

        Raises:
            BradfordWhiteConnectUnknownException: If a 401 status code is
            received after logging in. requests.exceptions.HTTPError:
            If a non-401 status code is received.
        """

        # trunk-ignore(flake8/E501)
        async with self.session.post(uri, headers=headers, data=data) as response:
            # catch access denied errors and attempt to re-authenticate
            if response.status == 401:
                # if we're already retrying after logging in,
                # raise an exception
                if retrying_after_login:
                    raise BradfordWhiteConnectUnknownException(
                        "Received status code 401 after logging in"
                    )

                # update headers with new token
                logger.debug("Token may be expired - retrying login")
                await self.authenticate()
                headers["authorization"] = f"auth_token {self.token}"

                # retry the request
                return await self.http_post_request(
                    uri, headers, data, retrying_after_login=True
                )

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
