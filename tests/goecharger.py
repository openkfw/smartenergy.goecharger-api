"""Test cases for the main Go-eCharger module"""
import unittest

from unittest import mock
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
}
EXPECTED_MAPPED_RESPONSE = {
    "adapter": "unknown",
    "allowed_ampere": None,
    "cable_lock_mode": 0,
    "cable_max_current": 0,
    "car_consumption": 12.0,
    "car_status": "Charger ready, no vehicle",
    "charger_absolute_max_current": 16,
    "charger_access": "open",
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
    "energy_total": 1234.5,
    "firmware": "058.2",
    "i_l1": 0.0,
    "i_l2": 0.0,
    "i_l3": 0.0,
    "lf_l1": 0,
    "lf_l2": 0,
    "lf_l3": 0,
    "lf_n": 0,
    "min_charging_current": 10,
    "min_charging_time": 100000,
    "p_all": 0.0,
    "p_l1": 0.0,
    "p_l2": 0.0,
    "p_l3": 0.0,
    "p_n": 0.0,
    "phase_switch_mode": 1,
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

    if args[0] == "http://localhost:3000/api/status?age=50000":
        return MockResponse(REQUEST_RESPONSE, 200)

    if args[0] == "http://localhost:3001/api/status?age=50000":
        return MockResponse(None, 200)

    return MockResponse(None, 404)


class Test(unittest.TestCase):
    """Unit tests testing mapping of the response and API calls."""

    def test_status_mapping_response(self) -> None:
        """Test if response mapper correctly transforms property names"""
        status_mapper = GoeChargerStatusMapper()
        self.assertDictEqual(
            status_mapper.map_api_status_response(REQUEST_RESPONSE),
            EXPECTED_MAPPED_RESPONSE,
        )

    @mock.patch(
        "requests.get",
        mock.Mock(side_effect=mocked_requests_get),
    )
    def test_request_status_ok(self) -> None:
        """Test if status request returns a valid response in case the API call succeeds"""
        self.maxDiff = None
        api = GoeChargerApi("http://localhost:3000", "TOKEN")
        self.assertDictEqual(
            api.request_status(),
            EXPECTED_MAPPED_RESPONSE,
        )

    @mock.patch(
        "requests.get",
        mock.Mock(side_effect=mocked_requests_get),
    )
    def test_request_status_error(self) -> None:
        """Test if status request raises an error in case the API call fails"""
        api = GoeChargerApi("http://localhost:3001", "TOKEN")
        self.assertRaises(RuntimeError, api.request_status)


if __name__ == "__main__":
    unittest.main()
