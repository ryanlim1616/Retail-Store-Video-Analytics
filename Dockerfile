FROM sgtwilko/rpi-raspbian-opencv
RUN apt-get update && apt-get install git
RUN pip3 install cvui
RUN apt-get install -qqy x11-apps
ENV DISPLAY :0
RUN git clone https://github.com/BrightTux/Retail-Store-Video-Analytics.git
RUN sudo usermod -a -G video $(whoami)
