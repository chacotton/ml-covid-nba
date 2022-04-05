#!/bin/bash

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  sudo systemctl start docker
  sudo docker build -t helloapp:v1 .
  sudo docker run -v $(pwd):/docker helloapp:v1
  sudo systemctl stop docker
fi
