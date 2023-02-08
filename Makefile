.PHONY: install

install:
	pip install -U pip
	pip install openmim torch
	mim install mmcv-full
	mim install mmdet
	mim install mmpose
	mim install -r requirements.txt