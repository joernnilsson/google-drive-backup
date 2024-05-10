#!/usr/bin/env bash

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