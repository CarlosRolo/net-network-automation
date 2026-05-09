"""
validator.py — Validación post-deploy con NAPALM
"""
import os
from napalm import get_network_driver
from dotenv import load_dotenv

load_dotenv()

DEVICES = [
    {"host": "192.168.100.1", "name": "R1", "driver": "ios"},
    {"host": "192.168.100.2", "name": "R2", "driver": "ios"},
]


def validate_device(device: dict) -> dict:
    driver = get_network_driver(device["driver"])
    dev = driver(
        hostname=device["host"],
        username=os.getenv("NET_USERNAME", "admin"),
        password=os.getenv("NET_PASSWORD", "admin123"),
        optional_args={"secret": os.getenv("NET_SECRET", "admin123")},
    )

    result = {"device": device["name"], "checks": {}}

    try:
        dev.open()
        facts = dev.get_facts()
        interfaces = dev.get_interfaces()

        result["checks"]["hostname_ok"] = facts["hostname"] == device["name"]
        result["checks"]["interfaces_up"] = sum(
            1 for iface in interfaces.values() if iface["is_up"]
        )
        result["checks"]["facts"] = {
            "os_version": facts["os_version"],
            "uptime": facts["uptime"],
            "serial_number": facts["serial_number"],
        }
        result["status"] = "validated"
        dev.close()
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


if __name__ == "__main__":
    for device in DEVICES:
        result = validate_device(device)
        print(f"\n[{device['name']}] Status: {result['status']}")
        if "checks" in result:
            for check, value in result["checks"].items():
                print(f"  {check}: {value}")
