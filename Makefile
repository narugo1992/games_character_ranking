.PHONY: install

install:
	pip install -U pip
	pip install openmim torch
	mim install -r requirements.txt