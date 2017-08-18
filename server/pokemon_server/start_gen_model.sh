#!/bin/bash
docker run --user="$(id -u):$(id -g)" \
           -v `pwd`:/opt/src  \
           -v `pwd`:/opt/game  \
           -it pokemon:lastest \
           "./gen_model.sh"
