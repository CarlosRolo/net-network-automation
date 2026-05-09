# NET-04: Network Automation with Netmiko + Ansible

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Netmiko](https://img.shields.io/badge/Netmiko-4.3.0-green)
![Ansible](https://img.shields.io/badge/Ansible_Core-2.16-red?logo=ansible)
![NAPALM](https://img.shields.io/badge/NAPALM-4.1.0-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

Automated configuration and management of Cisco IOS routers and switches using Python (Netmiko), Ansible, NAPALM, and Jinja2 templates. Includes mass SSH config push, automated Git-versioned backups, post-deploy validation, and a Rich terminal dashboard.

---

## Architecture

Inventory (YAML) -> Jinja2 Templates -> Netmiko SSH Push -> Cisco IOS Devices -> NAPALM Validation + Git Backup -> Rich Terminal Dashboard

## Features

- Mass SSH configuration push to multiple devices in parallel (ThreadPoolExecutor)
- Jinja2 templates for OSPF, VLANs and ACLs
- Automated backup with Git versioning
- Post-deploy validation with NAPALM
- Rich terminal dashboard showing device status
- Ansible playbooks for full topology deployment

## Lab Topology

PC1 -- SW1 -- R1 -- R2 -- SW2 -- PC2

| Device | IP | Role |
|--------|-----|------|
| R1 | 192.168.100.1 | Core Router |
| R2 | 192.168.100.2 | Core Router |
| SW1 | 192.168.100.11 | Access Switch |
| SW2 | 192.168.100.12 | Access Switch |

Topology simulated in Packet Tracer with Cisco IOS 2911 routers and 2960 switches.

## Project Structure

net-network-automation/
├── netmiko_scripts/scripts/push_config.py   # Mass SSH push with threading
├── netmiko_scripts/scripts/backup.py        # Automated backup + Git commit
├── netmiko_scripts/scripts/validate.py      # Basic validation
├── ansible/inventory/hosts.yml              # Device inventory
├── ansible/playbooks/deploy.yml             # Full deployment playbook
├── ansible/playbooks/backup.yml             # Backup playbook
├── templates/ospf.j2                        # OSPF Jinja2 template
├── templates/vlan.j2                        # VLAN Jinja2 template
├── templates/acl.j2                         # ACL Jinja2 template
├── napalm/validator.py                      # Post-deploy validation
├── dashboard/status.py                      # Rich terminal dashboard
└── backup/                                  # Git-versioned config backups

## Quick Start

git clone https://github.com/CarlosRolo/net-network-automation.git
cd net-network-automation
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

Edit .env with your device credentials:
NET_USERNAME=admin
NET_PASSWORD=yourpassword
NET_SECRET=yoursecret

## Usage

make push       # Push configs to all devices via SSH
make backup     # Backup all configs + auto Git commit
make validate   # Post-deploy validation with NAPALM
make dashboard  # Rich terminal status dashboard

## Stack

| Tool | Purpose |
|------|---------|
| Netmiko 4.3 | SSH connectivity and config push |
| NAPALM 4.1 | Post-deploy validation and facts |
| Ansible Core 2.16 | Playbook-based deployment |
| Jinja2 | Configuration templating |
| Rich | Terminal dashboard |
| Git | Versioned config backups |

## Author

**Carlos David Rodriguez Lopez**  
Telematic Engineer — ESPOCH  
Riobamba, Chimborazo, Ecuador  
Manta, Manabí, Ecuador  
GitHub: [github.com/CarlosRolo](https://github.com/CarlosRolo)  
LinkedIn: [linkedin.com/in/carlosdrodriguezl](https://linkedin.com/in/carlosdrodriguezl)

## License

MIT License — see [LICENSE](LICENSE)
