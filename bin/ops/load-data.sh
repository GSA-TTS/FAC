#!/bin/bash
git config --global http.proxy "$https_proxy"
git clone https://github.com/GSA-TTS/fac-historic-public-csvs.git
./fac-historic-public-csvs/wait-and-load.sh
