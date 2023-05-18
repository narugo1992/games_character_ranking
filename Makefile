.PHONY: install

PYTHON ?= $(shell which python)

install:
	pip install -r requirements.txt

clean:
	rm -rf images

relocal:
	$(PYTHON) -m ranking relocal
