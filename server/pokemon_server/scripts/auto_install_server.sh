#!/bin/sh
for i in `seq $1 $2`;
do
echo $i'\n\n\n\n\n' | ./install_server.sh;
done;
