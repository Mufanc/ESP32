.PHONY : run ls flash
.ONESHELL :

DEVICE := /dev/ttyUSB0

run:
	[ -z "$$VIRTUAL_ENV" ] && source venv/bin/activate
	python scripts/upload_files.py src/main.py src ${DEVICE}
	minicom --device ${DEVICE}

ls:
	ampy -p ${DEVICE} ls

flash:
	python -m esptool --chip esp32 erase_flash
	python -m esptool --chip esp32 write_flash -z 0x1000 firmware/*.bin
