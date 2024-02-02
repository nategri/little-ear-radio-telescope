FROM arm64v8/ubuntu:jammy

RUN apt update && \
	DEBIAN_FRONTEND="noninteractive" apt install -y \
	cmake \
	doxygen \
	g++ \
	gir1.2-gtk-3.0 \
	git \
	libboost-all-dev \
	libfftw3-dev \
	libgmp3-dev \
	liblog4cpp5-dev \
	libqwt-qt5-dev \
	python3-click-plugins \
	python3-distutils \
	python3-gi-cairo \
	python3-mako \
	python3-numpy \
	python3-pip \
	python3-pyqt5 \
	python3-pyqtgraph \
	python3-scipy \
	python3-yaml \
	qtbase5-dev \
	clang-format \
	dbus-x11 \
	libiio-utils \
  libavahi-client-dev \
	gnuradio \
	inetutils-ping 

RUN pip install astropy
RUN pip install pybaselines

ENV DISPLAY host.docker.internal:0
ENV GRC_BLOCKS_PATH /usr/local/share/gnuradio/grc/blocks
ENV PYTHONPATH /usr/local/lib/python3/dist-packages/

ENV RT_LON -122.45898
ENV RT_LAT 45.41762

RUN mkdir -p /root/radio-telescope
WORKDIR /root/radio-telescope
