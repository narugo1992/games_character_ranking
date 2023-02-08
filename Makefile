.PHONY: install

install:
	pip install -U pip
	pip install openmim torch
	mim install mmcv-full==1.3.16
	mim install mmdet==2.18.0
	mim install mmpose==0.20.0
	pip install anime-face-detector==0.0.4
	pip install -r requirements.txt