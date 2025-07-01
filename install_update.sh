#!/usr/bin/env bash

# Google Drive Backup Service Installer/Updater
# ===========================================
# This script can be used to:
#   - Perform initial installation of the Google Drive backup service
#   - Update the service to a newer version
#
# The script will:
#   1. Pull the latest Docker image from GitHub Container Registry
#   2. Stop and remove any existing container
#   3. Start a new container with the updated image
#   4. Mount the necessary volumes (backup items, config files)
#   5. Configure automatic restart unless manually stopped
#
# Prerequisites:
#   - Docker must be installed and running
#   - config.yaml must be properly configured
#   - service_account.json must be present and valid
#   - Backup items specified in config.yaml must exist

set -x
set -e

IMAGE="ghcr.io/joernnilsson/google-drive-backup:master"
CONTAINER_NAME="google-drive-backup"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

# Build list of items
yaml_file="config.yaml"

items=$(sed -n '/items:/,$p' $yaml_file | grep -v 'items:' | grep -e '- ' | sed 's/ - //')

ITEMS=""
for item in $items; do
    ITEMS+="-v $(readlink -f $item):/backup/$item:ro "
done

# Update and restart container
docker pull $IMAGE || true
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true

docker run --restart unless-stopped -d --name $CONTAINER_NAME -ti $ITEMS \
	-v $(readlink -f config.yaml):/config/config.yaml \
	-v $(readlink -f service_account.json):/config/service_account.json \
	$IMAGE