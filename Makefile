.PHONY: install

install:
	pip install -U pip
	pip install openmim==0.1.5 torch==1.10.0 torchvision==0.11.1
	mim install mmcv-full==1.3.16
	mim install mmdet==2.18.0
	mim install mmpose==0.20.0
	pip install anime-face-detector==0.0.4
	pip install -r requirements.txt