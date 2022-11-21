"""Go-eCharger API module, documentation: https://go-e.co/app/api.pdf"""

import threading
from typing import Literal
from json.decoder import JSONDecodeError
import requests

from .validations import validate_empty_string


# pylint: disable=too-many-locals
class GoeChargerStatusMapper:
    """
    Mapping class to map properties into more human readable names.
    """

    def map_api_status_response(self, status: dict) -> dict:
        """
        Map response from the API call into more human readable names.
        """

        car_status = (
            GoeChargerApi.GO_CAR_STATUS.get(str(status.get("car"))) or "unknown"
        )
        charger_max_current = int(status.get("amp", 0))
        charger_force_charging = GoeChargerApi.GO_FORCE_CHARGING.get(
            status.get("frc") or 0
        )
        min_charging_current_limit = int(status.get("mca", 0))
        max_charging_current_limit = int(status.get("ama", 0))
        charger_err = GoeChargerApi.GO_ERR.get(str(status.get("err"))) or "unknown"
        charger_access = GoeChargerApi.GO_ACCESS.get(status.get("acs", False))
        charging_allowed = (
            GoeChargerApi.GO_CHARGING_ALLOWED.get(status.get("alw")) or "unknown"
        )
        cable_max_current = int(status.get("cbl", 0) or 0)
        cable_lock_mode = int(status.get("ust", 0))

        def value_or_null(array, index):
            try:
                return array[index]
            except IndexError:
                return 0

        phase = status.get("pha", [])
        pre_contactor_l3 = value_or_null(phase, 0)
        pre_contactor_l2 = value_or_null(phase, 1)
        pre_contactor_l1 = value_or_null(phase, 2)
        post_contactor_l3 = value_or_null(phase, 3)
        post_contactor_l2 = value_or_null(phase, 4)
        post_contactor_l1 = value_or_null(phase, 5)

        phase_switch_mode = status.get("psm", 0)
        phases_number_connected = status.get("pnp", 0)

        if len(status.get("tma", [])) > 0:
            t_0 = float(value_or_null(status.get("tma", []), GoeChargerApi.TMA_0))
            t_1 = float(value_or_null(status.get("tma", []), GoeChargerApi.TMA_1))
            t_2 = float(value_or_null(status.get("tma", []), GoeChargerApi.TMA_2))
            t_3 = float(value_or_null(status.get("tma", []), GoeChargerApi.TMA_3))
            charger_temp = round(int((t_0 + t_1 + t_2 + t_3) / 4), 2)
        else:
            charger_temp = int(
                status.get("tmp", 0)
            )  # Deprecated: Just for chargers with old firmware

        current_session_charged_energy = round(int(status.get("dws", 0)) / 360000.0, 5)
        charge_limit = int(status.get("dwo", 0) or 0)
        adapter = GoeChargerApi.GO_ADAPTER.get(status.get("adi")) or "unknown"
        unlocked_by_card = int(status.get("uby", 0))
        energy_total = int(status.get("eto", 0))
        energy_by_token = {
            "token_a": int(status.get("eca", 0)),
            "token_r": int(status.get("ecr", 0)),
            "token_d": int(status.get("ecd", 0)),
            "token_4": int(status.get("ec4", 0)),
            "token_5": int(status.get("ec5", 0)),
            "token_6": int(status.get("ec6", 0)),
            "token_7": int(status.get("ec7", 0)),
            "token_8": int(status.get("ec8", 0)),
            "token_9": int(status.get("ec9", 0)),
            "token_1": int(status.get("ec1", 0)),
        }
        wifi = (
            "connected"
            if str(status.get("wst")) == 3
            else "unknown"
            if status.get("wst") is None
            else "not connected"
        )
        firmware = status.get("fwv", "unknown")
        serial_number = status.get("sse", "unknown")
        wifi_enabled = (
            "on"
            if status.get("wen") == "true"
            else "off"
            if status.get("wen") == "false"
            else "unknown"
        )
        timezone_offset = int(status.get("tof", 0)) - 100
        timezone_dst_offset = int(status.get("tds", 0))

        return {
            "car_status": car_status,
            "charger_max_current": charger_max_current,
            "charger_force_charging": charger_force_charging,
            "min_charging_current_limit": min_charging_current_limit,
            "max_charging_current_limit": max_charging_current_limit,
            "charger_err": charger_err,
            "charger_access": charger_access,
            "charging_allowed": charging_allowed,
            "cable_lock_mode": cable_lock_mode,
            "cable_max_current": cable_max_current,
            "pre_contactor_l1": pre_contactor_l1,
            "pre_contactor_l2": pre_contactor_l2,
            "pre_contactor_l3": pre_contactor_l3,
            "post_contactor_l1": post_contactor_l1,
            "post_contactor_l2": post_contactor_l2,
            "post_contactor_l3": post_contactor_l3,
            "phase_switch_mode": phase_switch_mode,
            "phases_number_connected": phases_number_connected,
            "charger_temp": charger_temp,  # Deprecated: Just for chargers with old firmware
            "charger_temp0": round(
                float(value_or_null(status.get("tma", []), GoeChargerApi.TMA_0)), 2
            ),
            "charger_temp1": round(
                float(value_or_null(status.get("tma", []), GoeChargerApi.TMA_1)), 2
            ),
            "charger_temp2": round(
                float(value_or_null(status.get("tma", []), GoeChargerApi.TMA_2)), 2
            ),
            "charger_temp3": round(
                float(value_or_null(status.get("tma", []), GoeChargerApi.TMA_3)), 2
            ),
            "current_session_charged_energy": round(current_session_charged_energy, 5),
            "charging_limit": charge_limit,
            "adapter": adapter,
            "unlocked_by_card": unlocked_by_card,
            "energy_total": energy_total,
            "energy_by_token": energy_by_token,
            "wifi": wifi,
            "u_l1": int(value_or_null(status.get("nrg", []), GoeChargerApi.U_L1)),
            "u_l2": int(value_or_null(status.get("nrg", []), GoeChargerApi.U_L2)),
            "u_l3": int(value_or_null(status.get("nrg", []), GoeChargerApi.U_L3)),
            "u_n": int(value_or_null(status.get("nrg", []), GoeChargerApi.U_N)),
            "i_l1": int(value_or_null(status.get("nrg", []), GoeChargerApi.I_L1))
            / 10.0,
            "i_l2": int(value_or_null(status.get("nrg", []), GoeChargerApi.I_L2))
            / 10.0,
            "i_l3": int(value_or_null(status.get("nrg", []), GoeChargerApi.I_L3))
            / 10.0,
            "p_l1": int(value_or_null(status.get("nrg", []), GoeChargerApi.P_L1))
            / 10.0,
            "p_l2": int(value_or_null(status.get("nrg", []), GoeChargerApi.P_L2))
            / 10.0,
            "p_l3": int(value_or_null(status.get("nrg", []), GoeChargerApi.P_L3))
            / 10.0,
            "p_n": int(value_or_null(status.get("nrg", []), GoeChargerApi.P_N)) / 10.0,
            "p_all": int(value_or_null(status.get("nrg", []), GoeChargerApi.P_ALL))
            / 100.0,
            "lf_l1": int(value_or_null(status.get("nrg", []), GoeChargerApi.LF_L1)),
            "lf_l2": int(value_or_null(status.get("nrg", []), GoeChargerApi.LF_L2)),
            "lf_l3": int(value_or_null(status.get("nrg", []), GoeChargerApi.LF_L3)),
            "lf_n": int(value_or_null(status.get("nrg", []), GoeChargerApi.LF_N)),
            "firmware": firmware,
            "serial_number": serial_number,
            "wifi_enabled": wifi_enabled,
            "timezone_offset": timezone_offset,
            "timezone_dst_offset": timezone_dst_offset,
            "allowed_ampere": int(status.get("acu", 0))
            if status.get("acu") == "null"
            else None,
            "energy_since_car_connected": float(status.get("wh", 0)),
            "charging_duration": status.get("cdi", None),
            "min_charging_time": int(status.get("fmt", 0)),
            "car_consumption": float(status.get("cco", 0)),
            "rssi_signal_strength": int(status.get("rssi", 0)),
        }


class GoeChargerApi:
    """
    Class providing methods for querying the status and setting of the parameters
    via API calls.
    """

    def __init__(
        self, host: str, token: str, timeout: int = 5, wait: bool = False
    ) -> None:
        validate_empty_string(host, "host")
        validate_empty_string(token, "token")
        self.host: str = host
        self.token: str = token
        self.timeout: int = timeout
        self.wait: bool = wait

    GO_CAR_STATUS: dict[str, str] = {
        "1": "Charger ready, no car connected",
        "2": "Car is charging",
        "3": "Car connected, authentication required",
        "4": "Charging finished, car can be disconnected",
    }

    GO_ADAPTER: dict[str, str] = {
        "0": "No Adapter",
        "1": "16A-Adapter",
        "false": "No Adapter",
        "true": "16A-Adapter",
    }

    U_L1: Literal[0] = 0
    U_L2: Literal[1] = 1
    U_L3: Literal[2] = 2
    U_N: Literal[3] = 3
    I_L1: Literal[4] = 4
    I_L2: Literal[5] = 5
    I_L3: Literal[6] = 6
    P_L1: Literal[7] = 7
    P_L2: Literal[8] = 8
    P_L3: Literal[9] = 9
    P_N: Literal[10] = 10
    P_ALL: Literal[11] = 11
    LF_L1: Literal[12] = 12
    LF_L2: Literal[13] = 13
    LF_L3: Literal[14] = 14
    LF_N: Literal[15] = 15

    TMA_0: Literal[0] = 0
    TMA_1: Literal[1] = 1
    TMA_2: Literal[2] = 2
    TMA_3: Literal[3] = 3

    GO_ERR: dict[str, str] = {
        "0": "OK",
        "1": "RCCB",
        "3": "PHASE",
        "8": "NO_GROUND",
        "10": "INTERNAL",
    }

    GO_ACCESS: dict[int, str] = {0: True, 1: False}

    GO_CHARGING_ALLOWED: dict[str | bool, str] = {
        "0": "off",
        "1": "on",
        False: "off",
        True: "on",
    }
    GO_FORCE_CHARGING: dict[int, str] = {0: "neutral", 1: "off", 2: "on"}

    def __query_status_api(self) -> dict:
        """
        Generic method to get status with all parameters via the API call.
        """
        try:
            headers = {"Authorization": f"Basic {self.token}"}

            status_request = requests.get(
                f"{self.host}/api/status",
                headers=headers,
                timeout=self.timeout,
            )
            status = status_request.json()
            return status
        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
        ):
            return {"success": False, "msg": "Request couldn't connect or timed out"}

    def __verify_set_parameter(self, parameter, value, retry) -> None:
        """
        Optional method to check if the changed parameter was really changed.
        Setting of a parameter doesn't provide a real feedback, but we can utilize
        the query status API to verify it.
        """
        status = self.__query_status_api()
        fetched_value_int = int(status.get(parameter))
        value_int = int(value)

        if fetched_value_int != value_int and retry == 0:
            raise ValueError(
                f"""Couldn't verify {parameter}, expected value={value_int},
                 received value={fetched_value_int}"""
            )

        if fetched_value_int != value_int and retry > 0:
            threading.Timer(
                1.0, self.__verify_set_parameter, [parameter, value, retry - 1]
            ).start()

    def __set_parameter(self, parameter, value) -> dict:
        """
        Generic method to set any parameter and call the API.
        """
        try:
            headers = {"Authorization": f"Basic {self.token}"}

            payload = {}
            payload[parameter] = value
            set_request = requests.get(
                f"{self.host}/api/set",
                headers=headers,
                params=payload,
                timeout=self.timeout,
            )

            if self.wait:
                self.__verify_set_parameter(parameter, value, 5)

            return GoeChargerStatusMapper().map_api_status_response(set_request.json())
        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
        ):
            return {"success": False, "msg": "Request couldn't connect or timed out"}

    def set_force_charging(self, allow) -> dict:
        """
        Sets the force charging.
        0 - neutral
        1 - off
        2 - on
        """
        if allow:
            return self.__set_parameter("frc", 2)

        return self.__set_parameter("frc", 1)

    def set_max_current(self, current) -> dict:
        """
        Sets the current in Amperes. Minimum is 0, maximum is 32 Amperes.
        """
        if current < 0:
            return self.__set_parameter("amp", str(0))
        if current > 32:
            return self.__set_parameter("amp", str(32))

        return self.__set_parameter("amp", str(current))

    def set_phase(self, phase) -> dict | None:
        """
        Sets the phase.
        0 - auto
        1 - 1 phase
        2 - 3 phases
        """
        if phase in [0, 1, 2]:
            return self.__set_parameter("psm", str(phase))

        raise ValueError(f"phase={phase} is unsupported")

    def set_access_control(self, status) -> dict | None:
        """
        Sets the access control.
        0 - open
        1 - wait
        """
        if status in [0, 1]:
            return self.__set_parameter("acs", str(status))

        raise ValueError(f"access control status={status} is unsupported")

    def set_transaction(self, status) -> dict | None:
        """
        Sets the access control.
        None - no transaction
        0 - without card - authenticate all users
        """
        if status is None:
            return self.__set_parameter("trx", None)

        if status in [0]:
            return self.__set_parameter("trx", str(status))

        raise ValueError(f"transaction status={status} is unsupported")

    def request_status(self) -> dict:
        """
        Call the GET API to retrieve a car status.
        """
        response = {}
        try:
            status = self.__query_status_api()
            if status is None or status.get("success") is False:
                if status and status.get("reason", None) == "Data is outdated":
                    return {"success": False, "msg": "Wallbox is offline"}

                raise RuntimeError(f"Request failed with: {status}")

            response = GoeChargerStatusMapper().map_api_status_response(status)
        except JSONDecodeError:
            response = GoeChargerStatusMapper().map_api_status_response({})
        return response
