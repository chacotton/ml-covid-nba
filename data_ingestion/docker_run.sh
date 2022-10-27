#!/bin/bash

today=$1
year=$2
sudo docker run -p 1521:1521 -e date="${today}" -e season="${year}" --mount type=volume,dst=/mnt/ml-nba,volume-opt=type=nfs,volume-opt=device=:/ml-nba,volume-opt=o=addr=10.0.0.161 modeling:v1
