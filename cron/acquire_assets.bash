#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 && pwd)"
PROJECT_ROOT=$(dirname "$DIR")
THUMBNAILS="$PROJECT_ROOT/data/thumbnails"
FAVICONS="$PROJECT_ROOT/data/favicons"
mkdir -p "$THUMBNAILS"
mkdir -p "$FAVICONS"

MYSQL="mysql --defaults-extra-file=${PROJECT_ROOT}/.mysql.cnf --skip-column-names --batch"

function do_cleanup() {
    message="$1"
    bid="$2"
    $MYSQL << EOF
UPDATE sc_bookmarks SET bThumbnailStatus = 'none' where bId = $bid;
EOF
    echo "$message"
    exit 1

}

exec 123> /var/lock/acquire_assets
flock -n 123 || exit 1

{
    $MYSQL << EOF
SELECT @bookmarkId := bId, bAddress from sc_bookmarks where bThumbnailStatus is null or bThumbnailStatus = 'none' order by bModified desc limit 1;
UPDATE sc_bookmarks SET bThumbnailStatus = 'pending' where bId = @bookmarkId;
EOF
} | while read -r bookmarkId address; do
    cd "$FAVICONS" || do_cleanup "Failed cd to $FAVICONS" "$bookmarkId"
    if ! favicon=$("$PROJECT_ROOT"/cron/download_favicon.bash "$address"); then
        do_cleanup "Favicon failure" "$bookmarkId"
    fi
    cd "$THUMBNAILS" || do_cleanup "Failed cd to $THUMBNAILS" "$bookmarkId"
    "$PROJECT_ROOT"/cron/download_thumbnail.bash -n "${bookmarkId}.png" "$address" || do_cleanup "Thumbnail failure" "$bookmarkId"

    $MYSQL << EOF
UPDATE sc_bookmarks SET bThumbnailStatus = 'complete', bFavicon = '$favicon' where bId = $bookmarkId;
EOF
done
