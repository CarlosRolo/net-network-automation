"""
backup.py — Backup automático de configs con versionado en Git
"""
import os
import subprocess
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from netmiko import ConnectHandler, NetmikoTimeoutException

load_dotenv()

DEVICES = [
    {"host": "192.168.100.1", "name": "R1"},
    {"host": "192.168.100.2", "name": "R2"},
    {"host": "192.168.100.11", "name": "SW1"},
    {"host": "192.168.100.12", "name": "SW2"},
]

BACKUP_DIR = Path("backup")
BACKUP_DIR.mkdir(exist_ok=True)

BASE_CREDS = {
    "device_type": "cisco_ios",
    "username": os.getenv("NET_USERNAME", "admin"),
    "password": os.getenv("NET_PASSWORD", "admin123"),
    "secret": os.getenv("NET_SECRET", "admin123"),
    "timeout": 15,
}


def backup_device(device: dict) -> str:
    conn_params = {**BASE_CREDS, "host": device["host"]}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = BACKUP_DIR / f"{device['name']}_{timestamp}.cfg"

    try:
        with ConnectHandler(**conn_params) as net_connect:
            net_connect.enable()
            config = net_connect.send_command("show running-config")
            with open(filename, "w") as f:
                f.write(config)
            print(f"[✓] Backup guardado: {filename}")
            return str(filename)
    except NetmikoTimeoutException:
        print(f"[✗] {device['name']}: TIMEOUT")
        return ""
    except Exception as e:
        print(f"[✗] {device['name']}: {e}")
        return ""


def git_commit_backups():
    subprocess.run(["git", "add", "backup/"], check=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    subprocess.run(
        ["git", "commit", "-m", f"backup: automated config backup {timestamp}"],
        check=True,
    )
    print("[✓] Backups commiteados en Git")


if __name__ == "__main__":
    print("Iniciando backup de dispositivos...")
    files = [backup_device(dev) for dev in DEVICES]
    files = [f for f in files if f]
    if files:
        git_commit_backups()
    print(f"\n✓ {len(files)} backups completados")
