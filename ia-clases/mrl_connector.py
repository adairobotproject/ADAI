#!/usr/bin/env python3
"""
MyRobotLab Connector (Minimal)
=============================

Utilities to talk to MyRobotLab (MRL) WebGui REST endpoints.

It attempts two strategies:
1) Direct REST call to /api/service/{service}.{sub}/method?params
2) JSON message POST to /api/messages (experimental)

If both fail, returns a string with the equivalent MRL script command
that can be pasted into MRL's Python console.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
import json

try:
    import requests  # type: ignore
except Exception:  # requests may not be present; GUI will handle fallback
    requests = None  # type: ignore


@dataclass
class MRLConfig:
    host: str = "127.0.0.1"
    port: int = 8888
    service: str = "i01"  # Default InMoov2 service name


class MRLConnector:
    def __init__(self, config: Optional[MRLConfig] = None) -> None:
        self.config = config or MRLConfig()

    def _base_url(self) -> str:
        return f"http://{self.config.host}:{self.config.port}"

    def test_connection(self) -> Tuple[bool, str]:
        if requests is None:
            return False, "Python 'requests' not installed"
        try:
            r = requests.get(self._base_url() + "/api/services", timeout=2.0)
            if r.status_code == 200:
                return True, "OK"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    def move_head(self, neck_deg: float, rothead_deg: float) -> Tuple[bool, str]:
        """Move head: neck (pitch), rothead (yaw)."""
        # Prefer InMoov2 service-level API: i01.moveHead(yaw, pitch)
        ok, msg = self._call_service_method(self.config.service, "moveHead", [rothead_deg, neck_deg])
        if ok:
            return ok, msg
        # Fallback to part service call
        return self._call_move_to(f"{self.config.service}.head", [neck_deg, rothead_deg])

    def move_right_arm(self, shoulder: float, rotate: float, bicep: float, elbow: float, omoplate: float) -> Tuple[bool, str]:
        # Prefer InMoov2 service-level API: i01.moveArm("right", s, r, b, e)
        ok, msg = self._call_service_method(self.config.service, "moveArm", ["right", shoulder, rotate, bicep, elbow])
        if ok:
            # try moveOmoplate optionally
            self.move_omoplate("right", omoplate)
            return ok, msg
        # Fallback: part service variants
        ok2, msg2 = self._call_move_to(f"{self.config.service}.rightArm", [shoulder, rotate, bicep, elbow, omoplate])
        if ok2:
            return ok2, msg2
        # Try sending as array single arg
        return self._call_move_to_array_arg(f"{self.config.service}.rightArm", [shoulder, rotate, bicep, elbow, omoplate])

    def move_left_arm(self, shoulder: float, rotate: float, bicep: float, elbow: float, omoplate: float) -> Tuple[bool, str]:
        # Prefer InMoov2 service-level API: i01.moveArm("left", s, r, b, e)
        ok, msg = self._call_service_method(self.config.service, "moveArm", ["left", shoulder, rotate, bicep, elbow])
        if ok:
            # try moveOmoplate optionally
            self.move_omoplate("left", omoplate)
            return ok, msg
        # Fallback: part service variants
        ok2, msg2 = self._call_move_to(f"{self.config.service}.leftArm", [shoulder, rotate, bicep, elbow, omoplate])
        if ok2:
            return ok2, msg2
        # Try sending as array single arg
        return self._call_move_to_array_arg(f"{self.config.service}.leftArm", [shoulder, rotate, bicep, elbow, omoplate])

    def move_omoplate(self, side: str, value: float) -> Tuple[bool, str]:
        # Try InMoov2 service-level moveOmoplate("left"/"right", value)
        return self._call_service_method(self.config.service, "moveOmoplate", [side, value])

    def _call_move_to(self, full_service: str, values: list) -> Tuple[bool, str]:
        # 1) Try /api/messages expecting an array of Message objects
        if requests is not None:
            try:
                payload = [{
                    "name": full_service,
                    "method": "moveTo",
                    "data": values,
                }]
                r = requests.post(
                    self._base_url() + "/api/messages",
                    json=payload,
                    timeout=2.0,
                    headers={"Content-Type": "application/json"},
                )
                if r.status_code == 200:
                    return True, "OK"
                last_err = f"HTTP {r.status_code}"
            except Exception as e:
                last_err = str(e)

            # 2) Try POST to service with JSON array body
            try:
                url = f"{self._base_url()}/api/service/{full_service}/moveTo"
                r = requests.post(
                    url,
                    json=values,
                    timeout=2.0,
                    headers={"Content-Type": "application/json"},
                )
                if r.status_code == 200:
                    return True, "OK"
                last_err = f"HTTP {r.status_code}"
            except Exception as e3:
                last_err = str(e3)

            # 3) Try RESTful GET only if all args numeric (avoid strings like 'left')
            try:
                if all(isinstance(v, (int, float)) for v in values):
                    args_path = "/".join(str(v) for v in values)
                    url = f"{self._base_url()}/api/service/{full_service}/moveTo/{args_path}"
                    r = requests.get(url, timeout=2.0)
                    if r.status_code == 200:
                        return True, "OK"
                    last_err = f"HTTP {r.status_code}"
            except Exception as e2:
                last_err = str(e2)
        else:
            last_err = "requests not available"

        # Fallback: return script command
        return False, self._script_for_move_to(full_service, values)

    def _script_for_move_to(self, full_service: str, values: list) -> str:
        # Produces something like: i01.head.moveTo(90, 90)
        return f"{full_service}.moveTo({', '.join(f'{v:.1f}' for v in values)})"

    def _call_move_to_array_arg(self, full_service: str, values: list) -> Tuple[bool, str]:
        # Some services expect a single array parameter moveTo([..])
        if requests is not None:
            try:
                payload = [{
                    "name": full_service,
                    "method": "moveTo",
                    "data": [values],
                }]
                r = requests.post(self._base_url() + "/api/messages", json=payload, timeout=2.0)
                if r.status_code == 200:
                    return True, "OK"
                last_err = f"HTTP {r.status_code}"
            except Exception as e:
                last_err = str(e)
        else:
            last_err = "requests not available"
        return False, self._script_for_move_to(full_service, values)

    def _call_service_method(self, service: str, method: str, args: list) -> Tuple[bool, str]:
        if requests is None:
            return False, "requests not available"
        last_err = "unknown"
        # /api/messages array
        try:
            payload = [{
                "name": service,
                "method": method,
                "data": args,
            }]
            r = requests.post(
                self._base_url() + "/api/messages",
                json=payload,
                timeout=2.0,
                headers={"Content-Type": "application/json"},
            )
            if r.status_code == 200:
                return True, "OK"
            last_err = f"HTTP {r.status_code}"
        except Exception as e:
            last_err = str(e)

        # Fallback GET only if all args numeric
        try:
            if all(isinstance(v, (int, float)) for v in args):
                args_path = "/".join(str(v) for v in args)
                url = f"{self._base_url()}/api/service/{service}/{method}/{args_path}"
                r = requests.get(url, timeout=2.0)
                if r.status_code == 200:
                    return True, "OK"
                last_err = f"HTTP {r.status_code}"
        except Exception as e2:
            last_err = str(e2)

        # Script
        return False, f"{service}.{method}({', '.join(repr(v) for v in args)})"


