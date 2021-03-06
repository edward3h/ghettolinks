#!/bin/bash
# shellcheck disable=SC2154

# This page displays the form for adding or editing a bookmark. Possibly pre-populated to support bookmarklet or extension

# shellcheck disable=SC1091
. ../../common.bash

common_header

cat << EOF
<form action="save.cgi" method="POST">
<input id="id" name="id" type="hidden" value="${FORM_id}">
<div id="container" class="card">
EOF

if ((${#MISSING[@]} > 0)); then
    echo '<div class="error">'
    echo "Missing required fields" "${MISSING[@]}"
    echo '</div>'
fi

cat << EOF
<div class="field">
<label for="address">Address <em>Required</em></label>
<input id="address" name="address" type="url" required="required" value="${FORM_address}">
</div>
<div class="field">
<label for="title">Title <em>Required</em></label>
<input id="title" name="title" type="text" required="required" value="${FORM_title}">
</div>
<div class="field">
<label for="description">Description</label>
<input id="description" name="description" type="text" value="${FORM_description}">
</div>
<div class="field">
<label for="tags">Tags <em>Comma separated</em></label>
<input id="tags" name="tags" type="text">
</div>
<div class="field buttons">
<label><span class="infoLabel">User</span></label>
<span class="user">${REMOTE_USER}</span>
<button id="cancel" type="button" onclick="history.back(-1)">Cancel</button>
<button id="save" name="save" type="submit">Save</button>
</div>
</div>
</form>
EOF

common_footer
