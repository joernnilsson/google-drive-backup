#!/usr/bin/env bash

set -x
set -e

wget https://raw.githubusercontent.com/joernnilsson/google-drive-backup/refs/heads/master/install_update.sh
wget https://raw.githubusercontent.com/joernnilsson/google-drive-backup/refs/heads/master/config_example.yaml -O config.yaml

echo "> Please edit the config.yaml file before running install_update.sh"

