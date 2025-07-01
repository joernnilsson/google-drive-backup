#!/usr/bin/env bash

# Google Drive Backup Service Bootstrap Script
# ===========================================
# This script is used for initial setup of the Google Drive backup service.
# It downloads the necessary files to get started:
#
# The script will:
#   1. Download the install_update.sh script from the GitHub repository
#   2. Download the config_example.yaml and save it as config.yaml
#   3. Prompt the user to edit the configuration before proceeding
#
# After running this script:
#   1. Edit config.yaml to configure your backup settings
#   2. Add your service_account.json file
#   3. Run install_update.sh to complete the installation
#
# This is typically the first script you run when setting up the backup service
# on a new system or in a new environment.

set -x
set -e

wget https://raw.githubusercontent.com/joernnilsson/google-drive-backup/refs/heads/master/install_update.sh
wget https://raw.githubusercontent.com/joernnilsson/google-drive-backup/refs/heads/master/config_example.yaml -O config.yaml
chmod +x install_update.sh

echo "> Please edit the config.yaml file before running install_update.sh"

