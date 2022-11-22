"""Test cases for the main Go-eCharger module"""
from functools import partial
from unittest import mock

import pytest

from src.goechargerv2.goecharger import GoeChargerStatusMapper, GoeChargerApi


REQUEST_RESPONSE = {
    "car": 1,
    "amp": 6,
    "frc": 0,
    "ama": 16,
    "err": 0,
    "acs": 0,
    "alw": True,
    "cbl": None,
    "ust": 0,
    "pha": [False, False, False, True, True, True],
    "psm": 1,
    "pnp": 1,
    "tma": [12.25, 24.875],
    "dwo": None,
    "adi": True,
    "eto": 12345,
    "wst": 3,
    "fwv": "058.2",
    "sse": "123",
    "wen": True,
    "tof": 10,
    "tds": 1,
    "acu": 6,
    "wh": 0,
    "cdi": {"type": 1, "value": 0},
    "mca": 10,
    "fmt": 100000,
    "cco": 12,
    "rssi": -40,
    "trx": None,
}
REQUEST_RESPONSE_SET = REQUEST_RESPONSE.copy()
EXPECTED_MAPPED_RESPONSE = {
    "adapter": "unknown",
    "allowed_ampere": None,
    "cable_lock_mode": 0,
    "cable_max_current": 0,
    "car_consumption": 12.0,
    "car_status": "Charger ready, no car connected",
    "charger_access": True,
    "charger_err": "OK",
    "charger_force_charging": "neutral",
    "charger_max_current": 6,
    "charger_temp": 9,
    "charger_temp0": 12.25,
    "charger_temp1": 24.88,
    "charger_temp2": 0.0,
    "charger_temp3": 0.0,
    "charging_allowed": "on",
    "charging_duration": {"type": 1, "value": 0},
    "charging_limit": 0.0,
    "current_session_charged_energy": 0.0,
    "energy_by_token": {
        "token_1": 0.0,
        "token_4": 0.0,
        "token_5": 0.0,
        "token_6": 0.0,
        "token_7": 0.0,
        "token_8": 0.0,
        "token_9": 0.0,
        "token_a": 0.0,
        "token_d": 0.0,
        "token_r": 0.0,
    },
    "energy_since_car_connected": 0.0,
    "energy_total": 12345,
    "firmware": "058.2",
    "i_l1": 0.0,
    "i_l2": 0.0,
    "i_l3": 0.0,
    "lf_l1": 0,
    "lf_l2": 0,
    "lf_l3": 0,
    "lf_n": 0,
    "min_charging_current_limit": 10,
    "max_charging_current_limit": 16,
    "min_charging_time": 100000,
    "p_all": 0.0,
    "p_l1": 0.0,
    "p_l2": 0.0,
    "p_l3": 0.0,
    "p_n": 0.0,
    "phase_switch_mode": 1,
    "phases_number_connected": 1,
    "post_contactor_l1": True,
    "post_contactor_l2": True,
    "post_contactor_l3": True,
    "pre_contactor_l1": False,
    "pre_contactor_l2": False,
    "pre_contactor_l3": False,
    "rssi_signal_strength": -40,
    "serial_number": "123",
    "timezone_dst_offset": 1,
    "timezone_offset": -90,
    "transaction": None,
    "u_l1": 0,
    "u_l2": 0,
    "u_l3": 0,
    "u_n": 0,
    "unlocked_by_card": 0,
    "wifi": "not connected",
    "wifi_enabled": "unknown",
}


# pylint: disable=unused-argument
def mocked_requests_get(*args, **kwargs):
    """Module handling mocked API requests"""

    class MockResponse:
        """Class handling mocked API responses"""

        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            """Return data as a JSON"""
            return self.json_data

    if args[0] == "http://localhost:3000/api/set":
        # pylint: disable=global-statement
        global REQUEST_RESPONSE_SET

        REQUEST_RESPONSE_SET = dict(
            REQUEST_RESPONSE_SET,
            **kwargs["params"],
        )

        return MockResponse(
            REQUEST_RESPONSE_SET,
            200,
        )

    if args[0] == "http://localhost:3000/api/status":
        if "set" in kwargs and kwargs["set"]:
            return MockResponse(REQUEST_RESPONSE_SET, 200)

        return MockResponse(REQUEST_RESPONSE, 200)

    if args[0] == "http://localhost:3001/api/status":
        return MockResponse(None, 200)

    if args[0] == "http://localhost:3002/api/status":
        return MockResponse(
            {"success": False, "reason": "Data is outdated", "age": 122},
            404,
        )

    return MockResponse(None, 404)


def test_status_mapping_response() -> None:
    """Test if response mapper correctly transforms property names"""
    status_mapper = GoeChargerStatusMapper()
    assert (
        status_mapper.map_api_status_response(REQUEST_RESPONSE)
        == EXPECTED_MAPPED_RESPONSE
    )


@mock.patch(
    "requests.get",
    mock.Mock(side_effect=mocked_requests_get),
)
def test_request_status_ok() -> None:
    """Test if status request returns a valid response in case the API call succeeds"""
    api = GoeChargerApi("http://localhost:3000", "TOKEN")
    assert api.request_status() == EXPECTED_MAPPED_RESPONSE


@mock.patch(
    "requests.get",
    mock.Mock(side_effect=mocked_requests_get),
)
def test_request_status_error() -> None:
    """Test if status request raises an error in case the API call fails"""
    api = GoeChargerApi("http://localhost:3001", "TOKEN")
    with pytest.raises(Exception) as exception_info:
        api.request_status()
    assert str(exception_info.value) == "Request failed with: None"


@mock.patch(
    "requests.get",
    mock.Mock(side_effect=mocked_requests_get),
)
def test_request_status_wallbox_offline() -> None:
    """Test if status request returns offline status when data is outdated."""
    api = GoeChargerApi("http://localhost:3002", "TOKEN")
    assert api.request_status() == {"success": False, "msg": "Wallbox is offline"}


@mock.patch(
    "requests.get",
    mock.Mock(side_effect=partial(mocked_requests_get, set=True)),
)
def test_request_set_wait() -> None:
    """Test if set request is changing the value and waiting for the change."""
    api = GoeChargerApi("http://localhost:3000", "TOKEN", wait=True)

    # test force charging
    changed_frc = api.set_force_charging(True)
    assert changed_frc["charger_force_charging"] == "on"

    # test max current
    changed_amp = api.set_max_current(14)
    assert changed_amp["charger_max_current"] == 14

    # change transaction change
    changed_trx_1 = api.set_transaction(0)
    assert changed_trx_1["transaction"] == 0

    # change transaction change
    changed_trx_2 = api.set_transaction(None)
    assert changed_trx_2["transaction"] == None
