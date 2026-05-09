"""
push_config.py — Push masivo de configuraciones a dispositivos Cisco via SSH
"""
import os
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from dotenv import load_dotenv
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from jinja2 import Environment, FileSystemLoader

load_dotenv()

DEVICES = [
    {"host": "192.168.100.1", "name": "R1", "type": "router"},
    {"host": "192.168.100.2", "name": "R2", "type": "router"},
    {"host": "192.168.100.11", "name": "SW1", "type": "switch"},
    {"host": "192.168.100.12", "name": "SW2", "type": "switch"},
]

BASE_CREDS = {
    "device_type": "cisco_ios",
    "username": os.getenv("NET_USERNAME", "admin"),
    "password": os.getenv("NET_PASSWORD", "admin123"),
    "secret": os.getenv("NET_SECRET", "admin123"),
    "timeout": 15,
}


def render_template(template_name: str, context: dict) -> str:
    env = Environment(loader=FileSystemLoader("templates/"))
    template = env.get_template(template_name)
    return template.render(**context)


def push_to_device(device: dict) -> dict:
    conn_params = {**BASE_CREDS, "host": device["host"]}
    result = {"device": device["name"], "host": device["host"], "status": "unknown", "output": ""}

    try:
        print(f"[→] Conectando a {device['name']} ({device['host']})...")
        with ConnectHandler(**conn_params) as net_connect:
            net_connect.enable()

            if device["type"] == "router":
                context = {
                    "hostname": device["name"],
                    "ospf_process": 1,
                    "router_id": f"1.1.1.{DEVICES.index(device) + 1}",
                    "network": "192.168.100.0",
                    "wildcard": "0.0.0.255",
                    "area": 0,
                }
                config = render_template("ospf.j2", context)
            else:
                context = {
                    "hostname": device["name"],
                    "vlans": [
                        {"id": 10, "name": "MANAGEMENT"},
                        {"id": 20, "name": "DATA"},
                        {"id": 30, "name": "VOICE"},
                    ],
                }
                config = render_template("vlan.j2", context)

            commands = [line for line in config.strip().splitlines() if line.strip()]
            output = net_connect.send_config_set(commands)
            net_connect.save_config()

            result["status"] = "success"
            result["output"] = output
            print(f"[✓] {device['name']} configurado correctamente")

    except NetmikoTimeoutException:
        result["status"] = "timeout"
        result["output"] = f"Timeout conectando a {device['host']}"
        print(f"[✗] {device['name']}: TIMEOUT")
    except NetmikoAuthenticationException:
        result["status"] = "auth_error"
        result["output"] = "Error de autenticación"
        print(f"[✗] {device['name']}: AUTH ERROR")
    except Exception as e:
        result["status"] = "error"
        result["output"] = str(e)
        print(f"[✗] {device['name']}: {e}")

    return result


def push_all(devices: list, max_workers: int = 4) -> list:
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(push_to_device, dev): dev for dev in devices}
        for future in as_completed(futures):
            results.append(future.result())
    return results


if __name__ == "__main__":
    print("=" * 50)
    print("NET-04 — Push masivo de configuraciones")
    print(f"Dispositivos: {len(DEVICES)} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    results = push_all(DEVICES)

    report_path = Path("netmiko_scripts/configs/push_report.json")
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)

    success = sum(1 for r in results if r["status"] == "success")
    print(f"\n✓ {success}/{len(DEVICES)} dispositivos configurados")
    print(f"Reporte guardado en: {report_path}")
