#!/bin/bash

# This page displays the form for adding or editing a bookmark. Possibly pre-populated to support bookmarklet or extension

# shellcheck disable=SC1091
. ../../common.bash

common_header

cat <<EOF
<form action="save.cgi" method="POST">
<div id="container" class="card">
<div class="field">
<label for="address">Address</label>
<input id="address" name="address" type="text">
</div>
</div>
</form>
EOF

common_footer
