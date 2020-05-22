#!/bin/bash

# This page displays the form for adding or editing a bookmark. Possibly pre-populated to support bookmarklet or extension

# cgibashopts is an external library which doesn't meet shellcheck requirements
# shellcheck disable=SC1091
. libs/cgibashopts/cgibashopts

# shellcheck source=common.bash
. common.bash

common_header

echo "Fix Me!"

common_footer