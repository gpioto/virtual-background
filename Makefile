run:
	xhost +local:docker

createFakeCam:
	sudo modprobe v4l2loopback -r
	sudo modprobe v4l2loopback devices=1 video_nr=20 card_label="v4l2loopback" exclusive_caps=1