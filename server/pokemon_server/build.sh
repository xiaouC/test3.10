#!/bin/bash
docker build --force-rm --build-arg uid=$(id -u) --build-arg gid=$(id -g) -t pokemon:lastest . || docker build --force-rm -t pokemon:lastest .
