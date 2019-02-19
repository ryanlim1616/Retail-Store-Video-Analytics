# Retail-Store-Video-Analytics

## Docker setup:
1. Create/Copy Dockerfile, insert the following:

```
FROM sgtwilko/rpi-raspbian-opencv
RUN apt-get update && apt-get install git vim nano
RUN pip3 install cvui
RUN pip3 install boto3
RUN pip3 install awscli
RUN apt-get install -qqy x11-apps
ENV DISPLAY :0
RUN git clone https://github.com/BrightTux/Retail-Store-Video-Analytics.git
RUN sudo usermod -a -G video $(whoami)
```

2. Build:

```
sudo docker build -t myretail .
```

3. Setup Parameters:
```
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
xauth nlist :0 | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -
```

4. Run the docker container:
```
sudo docker run -p 52022:22 -ti --device=/dev/vcsm --device=/dev/vchiq -v $XSOCK:$XSOCK -v $XAUTH:$XAUTH -e XAUTHORITY=$XAUTH myretail bash
```

*Note:*
The '-p 52022:22' command maps the docker 'myretail' container to the default
ssh port '22'.

5. To connect to the 'myretail' container via ssh for troubleshooting / maintainence:
```
ssh -X -p 52022 <user>@<remote server>
```
*Note:*
The '-X' parameter enables the forwarding of X11 windowing system.
For more info, refer to https://brighttux.github.io/posts/2019/02/ssh-with-gui/

-----------

## Usage Instructions:
1. Run `python3 setup.py` to setup the zones and entrance and exit locations.
	1. Zones are drawn using the "Set Zone" button, zones can be of
	different polygon shapes, depending on how many points were placed. You
	may name each of the zones after defining the zone.
	2. Entrance and Exit zones are created using 4 points.
		1. Top left corner box, Bottom right corner box, From, To
	3. Save the file after each zone/entrance/exit is created
2. Run `python3 retail.py` to execute the extraction program
3. The `secureCopy.py` program is used to backup the extracted JSON file, and
   ensure that the files are identical before deleting the original JSON file.
   Next, it will send the backed up file to the s3 bucket.

------------

## Other notes/reference material:
1. `https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html`
2. `https://docs.aws.amazon.com/cli/latest/reference/s3/index.html`
