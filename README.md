"# Retail-Store-Video-Analytics"

## Docker setup:
1. Create/Copy Dockerfile, insert the following:

`
FROM sgtwilko/rpi-raspbian-opencv
RUN apt-get update && apt-get install git
RUN pip3 install cvui
RUN apt-get install -qqy x11-apps
ENV DISPLAY :0
RUN git clone https://github.com/BrightTux/Retail-Store-Video-Analytics.git
RUN sudo usermod -a -G video $(whoami)
`


2. Build:

`
sudo docker build -t myretail .
`

3. Setup Parameters:
`
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
xauth nlist :0 | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -
`

4. Run the docker container:
`
sudo docker run -ti --device=/dev/vcsm --device=/dev/vchiq -v $XSOCK:$XSOCK -v $XAUTH:$XAUTH -e XAUTHORITY=$XAUTH myretail bash
`

## Usage Instructions:
1. Run setup.py to setup the zones and entrance and exit locations.
	1. Zones are drawn using the "Set Zone" button, zones can be of
	different polygon shapes, depending on how many points were placed. You
	may name each of the zones after defining the zone.
	2. Entrance and Exit zones are created using 4 points.
		1. Top left corner box, Bottom right corner box, From, To
	3. Save the file after each zone/entrance/exit is created
2. Run retail.py to execute the extraction program
