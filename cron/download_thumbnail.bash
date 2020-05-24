#!/bin/bash

function canexecute() {
    EPATH=$(type -path "$1")
    if [ -n "$EPATH" ] && [ -x "$EPATH" ]; then
        return 0
    else
        return 1
    fi
}

function print_usage() {
    if [ -n "$1" ]; then
        # error message
        echo "    Error: $1" >&2
        echo
    fi
    cat << EOM
    Usage: download_thumbnail.bash [options] <URL>
    Options:
        -h, --help: print this message and exit
        -n <name>, --filename <name>: Filename to save image as. png extension will be added if necessary
                                      Default: will attempt tp determine name from URL, or use 'thumbnail.png'
        -s <width>x<height>,
        --screen-size <width>x<height>: Size to use for the browser window.
                                        Default: 1024x400
        -t <width>x<height>,
        --thumbnail-size <width>x<height>: Maximum size of the thumbnail.
                                           Default: 192x192
EOM
    exit 1
}

function validate_size() {
    if grep -q -v -E '^[0-9]+[x,][0-9]$' <<< "$1"; then
        print_usage "Invalid size '$1'. Size should match '<width>x<height>' e.g. '1024x400'"
    fi
}

function parse_url() {
    # from: https://gist.github.com/joshisa/297b0bc1ec0dcdda0d1625029711fa24
    proto="$(echo "$1" | grep :// | sed -e's,^\(.*://\).*,\1,g')"
    # remove the protocol
    url="${1/$proto/}"
    # extract the user (if any)
    userpass="$(echo "$url" | grep @ | cut -d@ -f1)"
    pass="$(echo "$userpass" | grep : | cut -d: -f2)"
    if [ -n "$pass" ]; then
        user="$(echo "$userpass" | grep : | cut -d: -f1)"
    else
        user=$userpass
    fi

    # extract the host
    host="$(echo "${url/$user@/}" | cut -d/ -f1)"
    # by request - try to extract the port
    #port="$(echo $host | sed -e 's,^.*:,:,g' -e 's,.*:\([0-9]*\).*,\1,g' -e 's,[^0-9],,g')"
    # extract the path (if any)
    path="$(echo "$url" | grep / | cut -d/ -f2-)"
}

if ! canexecute "docker"; then
    print_usage "This script requires docker - please install it and try again"
fi

if ! canexecute "mogrify"; then
    print_usage "This script requires mogrify (ImageMagick) - please install it and try again"
fi

# defaults
SCREENSIZE="1024x400"
THUMBNAILSIZE="192x192"

# parse arguments
while (("$#")); do
    case "$1" in
        -h | --help)
            print_usage
            ;;
        -n | --filename)
            if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then
                FILENAME=$2
                shift 2
            else
                print_usage "Argument for $1 is missing"
            fi
            ;;
        -s | --screen-size)
            if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then
                SCREENSIZE=$2
                validate_size "$SCREENSIZE"
                shift 2
            else
                print_usage "Argument for $1 is missing"
            fi
            ;;

        -t | --thumbnail-size)
            if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then
                THUMBNAILSIZE=$2
                validate_size "$THUMBNAILSIZE"
                shift 2
            else
                print_usage "Argument for $1 is missing"
            fi
            ;;
        -*) # unsupported flags
            print_usage "Unsupported flag $1"
            ;;
        *) # positional arguments
            if [ -n "$URL" ]; then
                print_usage "URL is already set - only one URL may be specified"
            fi
            URL="$1"
            shift
            ;;
    esac
done

if [ -z "$URL" ]; then
    print_usage "Missing required argument URL"
fi

parse_url "$URL"

if [ -z "$FILENAME" ]; then
    FILENAME=$(echo "${host}_${path}" | sed -E -e 's/^[^A-Za-z0-9]+//;s/[^A-Za-z0-9]+$//;s/[^A-Za-z0-9]+/_/g;')
fi

if grep -v '\.png$' <<< "$FILENAME"; then
    FILENAME="$FILENAME.png"
fi

SCREENSIZE=$(tr 'x' ',' <<< "$SCREENSIZE")

docker container run -it --rm -v "$PWD:/usr/src/app" zenika/alpine-chrome --no-sandbox --screenshot="$FILENAME" --hide-scrollbars --window-size="$SCREENSIZE" "$URL"
mogrify -resize "$THUMBNAILSIZE" "$FILENAME"
echo "Thumbnail saved as '$FILENAME'"
