from unittest.mock import AsyncMock
from typing import cast

import aiohttp

from bradford_white_connect_client.client import BradfordWhiteConnectClient
from bradford_white_connect_client.types import Device, dataclass_from_api


DEVICE_PAYLOAD = {
    "product_name": "Water Heater",
    "model": "model",
    "dsn": "dsn",
    "oem_model": "oem-model",
    "sw_version": "1.0",
    "template_id": 1,
    "mac": "00:00:00:00:00:00",
    "unique_hardware_id": None,
    "lan_ip": "192.0.2.1",
    "connected_at": "2026-01-01T00:00:00Z",
    "key": 1,
    "lan_enabled": True,
    "connection_priority": ["wifi"],
    "has_properties": True,
    "product_class": None,
    "connection_status": "Online",
    "lat": "0",
    "lng": "0",
    "locality": None,
    "device_type": "Wifi",
    "dealer": None,
    "facility_uuid": None,
    "oem": "Bradford White",
    "transport_type": "Wifi",
    "a_future_api_field": "ignored",
}

PROPERTY_PAYLOAD = {
    "type": "property",
    "name": "tank_temp",
    "base_type": "integer",
    "read_only": True,
    "direction": "output",
    "scope": "user",
    "data_updated_at": "2026-01-01T00:00:00Z",
    "key": 2,
    "device_key": 1,
    "product_name": "Water Heater",
    "track_only_changes": True,
    "display_name": "Tank temperature",
    "host_sw_version": False,
    "time_series": True,
    "derived": False,
    "app_type": None,
    "recipe": None,
    "value": "120",
    "generated_from": None,
    "generated_at": None,
    "denied_roles": [],
    "ack_enabled": False,
    "retention_days": 30,
    "passthrough": False,
    "a_future_api_field": "ignored",
}


def make_client() -> BradfordWhiteConnectClient:
    session = cast(aiohttp.ClientSession, object())
    return BradfordWhiteConnectClient("user@example.com", "password", session=session)


async def test_get_devices_accepts_current_and_future_api_fields():
    client = make_client()
    client.http_get_request = AsyncMock(return_value=[{"device": DEVICE_PAYLOAD}])

    devices = await client.get_devices()

    assert len(devices) == 1
    assert devices[0].oem == "Bradford White"
    assert devices[0].transport_type == "Wifi"
    assert not hasattr(devices[0], "a_future_api_field")


async def test_get_device_properties_accepts_current_and_future_api_fields():
    client = make_client()
    client.http_get_request = AsyncMock(return_value=[{"property": PROPERTY_PAYLOAD}])

    device = dataclass_from_api(Device, DEVICE_PAYLOAD)
    properties = await client.get_device_properties(device)

    assert len(properties) == 1
    assert properties[0].property.passthrough is False
    assert not hasattr(properties[0].property, "a_future_api_field")


def test_generate_headers_includes_token_after_authentication():
    client = make_client()
    assert "authorization" not in client.generate_headers()

    client.token = "token"

    assert client.generate_headers()["authorization"] == "auth_token token"
