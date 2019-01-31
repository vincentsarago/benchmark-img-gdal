FROM remotepixel/amazonlinux-gdal:2.4.0

ENV \
  LANG=en_US.UTF-8 \
  LC_ALL=en_US.UTF-8

RUN yum install -y wget

RUN pip3 install pip -U
RUN pip3 install cython numpy --no-binary numpy

WORKDIR /tmp

COPY benchmark_img benchmark_img
COPY setup.py setup.py

RUN pip3 install . -U --no-binary rasterio

RUN cd /tmp; wget https://s3-us-west-2.amazonaws.com/remotepixel-pub/benchmark/RGB_cogeo.tif
RUN cd /tmp; wget https://s3-us-west-2.amazonaws.com/remotepixel-pub/benchmark/SRTM_cogeo.tif
