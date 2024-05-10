#!/usr/bin/env bash

set -x
set -e

IMAGE="local/google_drive_backup:latest"
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

docker run --restart unless-stopped --name $CONTAINER_NAME -d -ti \
-v /home/joern/dev/home/google-drive-backup/stryn:/backup/stryn:ro \
-v /home/joern/dev/home/google-drive-backup/README.md:/backup/README.md:ro \
-v /home/joern/file.txt:/backup//home/joern/file.txt:ro \
	$IMAGE