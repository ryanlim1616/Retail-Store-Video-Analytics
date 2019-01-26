FROM sgtwilko/rpi-raspbian-opencv
#CMD echo "Launching Video Retail Analytics Container"
RUN apt-get update && apt-get install git
RUN pip3 install cvui
RUN apt-get install -qqy x11-apps
ENV DISPLAY :0
RUN git clone https://github.com/BrightTux/Retail-Store-Video-Analytics.git
#CMD echo "Finish initiating, launching Container"
#CMD xeyes
RUN sudo usermod -a -G video $(whoami)

