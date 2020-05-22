#!/bin/bash

# This page displays the form for adding or editing a bookmark. Possibly pre-populated to support bookmarklet or extension

# shellcheck disable=SC1091
. ../common.bash

common_header

cat <<EOF
<form action="save.cgi" method="POST">
</form>
EOF

common_footer
