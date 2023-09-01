#!/bin/bash

#shopt -s extglob
#rm -rf /home/vcap/app/fac-historic-public-csvs/!(load_data.sh)
#ls | grep -xv "create-dumps.sh" | parallel rm /home/vcap/app/fac-historic-public-csvs/
git config --global http.proxy "$https_proxy"
git clone https://github.com/GSA-TTS/fac-historic-public-csvs.git
./fac-historic-public-csvs/create-dumps.sh
./fac-historic-public-csvs/wait-and-load.sh
