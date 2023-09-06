#!/bin/bash

# The following lines will enable extended glob, and allow us to remove /app, except load_data.sh in the event we want to reduce the task disk quota
#shopt -s extglob
#rm -rf /home/vcap/app/!(load_data.sh)
git config --global http.proxy "$https_proxy"
git clone https://github.com/GSA-TTS/fac-historic-public-csvs.git
cd fac-historic-public-csvs
export PATH=/home/vcap/deps/0/apt/usr/lib/postgresql/14/bin:$PATH
./create-dumps.sh
./wait-and-load.sh
