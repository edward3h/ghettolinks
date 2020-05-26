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
    Usage: download_favicon.bash [options] <URL>
    Options:
        -h, --help: print this message and exit
EOM
    exit 1
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
}

# parse arguments
while (("$#")); do
    case "$1" in
        -h | --help)
            print_usage
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
    FILENAME=$(echo "favicon_${host}" | sed -E -e 's/^[^A-Za-z0-9]+//;s/[^A-Za-z0-9]+$//;s/[^A-Za-z0-9]+/_/g;')
fi

if grep -v '\.png$' <<< "$FILENAME"; then
    FILENAME="$FILENAME.png"
fi

if [ -f "$FILENAME" ]; then
    echo "Favicon already exists as '$FILENAME'"
    exit 0
fi

wget -O "$FILENAME" "https://www.google.com/s2/favicons?domain=${host}" || exit 1
echo "Favicon saved as '$FILENAME'"
