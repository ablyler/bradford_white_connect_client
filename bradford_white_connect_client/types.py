"""Define package types."""

from dataclasses import dataclass, field, fields
from typing import Any, List, Mapping, Optional, Type, TypeVar

from dataclasses_json import LetterCase, dataclass_json


@dataclass
class Property:
    type: str
    name: str
    base_type: str
    read_only: bool
    direction: str
    scope: str
    data_updated_at: str
    key: int
    device_key: int
    product_name: str
    track_only_changes: bool
    display_name: str
    host_sw_version: bool
    time_series: bool
    derived: bool
    app_type: Optional[str]
    recipe: Optional[str]
    value: Optional[str]
    generated_from: Optional[str]
    generated_at: Optional[int]
    denied_roles: List[str]
    ack_enabled: bool
    retention_days: Optional[int]
    ack_status: Optional[str] = field(default=None)
    ack_message: Optional[str] = field(default=None)
    acked_at: Optional[str] = field(default=None)
    passthrough: Optional[bool] = field(default=None)


@dataclass
class PropertyWrapper:
    property: Property


@dataclass_json(letter_case=LetterCase.CAMEL)  # pyright: ignore[reportArgumentType]
@dataclass
class Device:
    product_name: str
    model: str
    dsn: str
    oem_model: str
    sw_version: str
    template_id: int
    mac: str
    unique_hardware_id: Optional[str]
    lan_ip: str
    connected_at: str
    key: int
    lan_enabled: bool
    connection_priority: List[str]
    has_properties: bool
    product_class: Optional[str]
    connection_status: str
    lat: str
    lng: str
    locality: Optional[str]
    device_type: str
    dealer: Optional[str]
    facility_uuid: Optional[str]
    oem: Optional[str] = field(default=None)
    transport_type: Optional[str] = field(default=None)
    properties: Optional[List[Property]] = field(default=None)


T = TypeVar("T", Device, Property)


def dataclass_from_api(cls: Type[T], payload: Mapping[str, Any]) -> T:
    """Build a dataclass from an API payload, ignoring additive API fields."""
    field_names = {item.name for item in fields(cls)}
    return cls(**{key: value for key, value in payload.items() if key in field_names})
