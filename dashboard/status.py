"""
status.py — Dashboard de estado de dispositivos con Rich
"""
import os
from datetime import datetime

from dotenv import load_dotenv
from netmiko import ConnectHandler, NetmikoTimeoutException
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

load_dotenv()

DEVICES = [
    {"host": "192.168.100.1", "name": "R1", "type": "Router"},
    {"host": "192.168.100.2", "name": "R2", "type": "Router"},
    {"host": "192.168.100.11", "name": "SW1", "type": "Switch"},
    {"host": "192.168.100.12", "name": "SW2", "type": "Switch"},
]

BASE_CREDS = {
    "device_type": "cisco_ios",
    "username": os.getenv("NET_USERNAME", "admin"),
    "password": os.getenv("NET_PASSWORD", "admin123"),
    "secret": os.getenv("NET_SECRET", "admin123"),
    "timeout": 8,
}

console = Console()


def check_device(device: dict) -> dict:
    conn_params = {**BASE_CREDS, "host": device["host"]}
    try:
        with ConnectHandler(**conn_params) as net_connect:
            net_connect.enable()
            version = net_connect.send_command("show version | include IOS")
            uptime = net_connect.send_command("show version | include uptime")
            return {
                "name": device["name"],
                "type": device["type"],
                "host": device["host"],
                "status": "UP",
                "version": version.strip()[:40] if version else "N/A",
                "uptime": uptime.strip()[:40] if uptime else "N/A",
            }
    except NetmikoTimeoutException:
        return {**device, "status": "TIMEOUT", "version": "-", "uptime": "-"}
    except Exception:
        return {**device, "status": "DOWN", "version": "-", "uptime": "-"}


def build_table(results: list) -> Table:
    table = Table(title="NET-04 — Estado de dispositivos", show_header=True)
    table.add_column("Dispositivo", style="bold")
    table.add_column("Tipo")
    table.add_column("IP")
    table.add_column("Estado", justify="center")
    table.add_column("Versión IOS", max_width=35)
    table.add_column("Uptime", max_width=30)

    for r in results:
        status_style = "green" if r["status"] == "UP" else "red"
        table.add_row(
            r["name"],
            r.get("type", ""),
            r["host"],
            Text(r["status"], style=status_style),
            r.get("version", "-"),
            r.get("uptime", "-"),
        )
    return table


if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold blue]NET-04 Network Automation Dashboard[/bold blue]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="blue"
    ))

    results = [check_device(dev) for dev in DEVICES]
    table = build_table(results)
    console.print(table)

    up_count = sum(1 for r in results if r["status"] == "UP")
    console.print(f"\n[bold]Dispositivos activos:[/bold] {up_count}/{len(DEVICES)}")
