#!/bin/bash

for PACKAGE in git-all python3.8 expect mysql
do
  sudo yum install -y $PACKAGE
done
sudo rm /usr/bin/python
sudo ln -s python3.8 /usr/bin/python
git config --global credential.helper store
git clone https://github.com/chacotton/ml-covid-nba.git
