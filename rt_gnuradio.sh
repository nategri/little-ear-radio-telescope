xhost + 127.0.0.1
docker run --network host -v "${PWD}":/root/radio-telescope --entrypoint gnuradio-companion -it radio-telescope-dev
