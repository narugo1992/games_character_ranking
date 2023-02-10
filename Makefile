.PHONY: install

PYTHON ?= $(shell which python)

install:
	pip install -U pip
	pip install openmim torch
	mim install -r requirements.txt

clean:
	rm -rf images

relocal:
	$(PYTHON) -m ranking relocal
