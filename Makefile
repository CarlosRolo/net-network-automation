.PHONY: help push backup validate dashboard

help:
	@echo "NET-04 Network Automation"
	@echo "  make push      - Push configs a todos los dispositivos"
	@echo "  make backup    - Backup automatico + commit Git"
	@echo "  make validate  - Validacion post-deploy con NAPALM"
	@echo "  make dashboard - Dashboard de estado en terminal"

push:
	python netmiko_scripts/scripts/push_config.py

backup:
	python netmiko_scripts/scripts/backup.py

validate:
	python napalm/validator.py

dashboard:
	python dashboard/status.py
