import os
import sys
import time

import pv
import requests
import serial
from pv import pvoutput


def require_env(name):
        value = os.getenv(name)
        if not value:
                raise ValueError("Missing required environment variable: " + name)
        return value


def run_once():
        pv.debug()

        serial_target = os.getenv("SERIAL_PORT", "COM6")
        pvoutput_api_key = require_env("PVOUTPUT_API_KEY")
        pvoutput_system_id = int(require_env("PVOUTPUT_SYSTEM_ID"))
        home_assistant_url = require_env("HOME_ASSISTANT_URL").rstrip("/")
        home_assistant_token = require_env("HOME_ASSISTANT_TOKEN")
        home_assistant_entity_id = os.getenv("HOME_ASSISTANT_ENTITY_ID", "sensor.solar_energy")

        port = serial.serial_for_url(serial_target, timeout=10, write_timeout=5)
        try:
                from pv import cms

                inv = cms.Inverter(port)
                print(inv)
                inv.reset()
                sn = inv.discover()
                if sn is None:
                        print("Inverter is not connected.")
                        return 1

                ok = inv.register(sn)
                if not ok:
                        print("Inverter registration failed.")
                        return 1

                print(inv.version())

                param_layout = inv.param_layout()
                parameters = inv.parameters(param_layout)
                for field in parameters:
                        print("%-10s: %s" % field)

                status_layout = inv.status_layout()
                status = inv.status(status_layout)
                for field in status:
                        print("%-10s: %s" % field)

                print("Sending to PVOutput")
                conn = pvoutput.Connection(pvoutput_api_key, pvoutput_system_id)

                status = dict(status)
                energy_today_wh = int(status["E-Today"] * 1000)
                print(energy_today_wh)
                conn.add_status(
                        time.strftime("%Y%m%d"),
                        time.strftime("%H:%M"),
                        energy_exp=energy_today_wh,
                        power_exp=status["Pac"],
                        cumulative=True,
                )
                print(conn.get_status())

                payload = {
                        "state": str(energy_today_wh),
                        "attributes": {
                                "unit_of_measurement": "Wh",
                                "device_class": "energy",
                                "state_class": "total_increasing",
                                "friendly_name": "Solar Energy",
                        },
                }
                headers = {
                        "Authorization": "Bearer " + home_assistant_token,
                }
                response = requests.post(
                        home_assistant_url + "/api/states/" + home_assistant_entity_id,
                        json=payload,
                        headers=headers,
                        timeout=20,
                )
                print(response.text)
                response.raise_for_status()
                return 0
        except Exception as inst:
                print("Serial connection or upload failed on %s: %s" % (serial_target, inst))
                return 1
        finally:
                port.close()


def main():
        interval_seconds = int(os.getenv("RUN_EVERY_SECONDS", "0"))
        if interval_seconds <= 0:
                return run_once()

        print("Running continuously every %d seconds" % interval_seconds)
        while True:
                started = time.time()
                run_once()
                elapsed = time.time() - started
                sleep_for = max(0.0, interval_seconds - elapsed)
                if sleep_for:
                        time.sleep(sleep_for)


if __name__ == "__main__":
        sys.exit(main())
