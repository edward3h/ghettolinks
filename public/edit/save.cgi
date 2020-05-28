#!/bin/bash
# shellcheck disable=SC2154
# shellcheck disable=SC2001

# This page saves results from adding or editing a bookmark
# shellcheck disable=SC1091
. ../../common.bash

MISSING=()

if [ -z "$FORM_address" ]; then
    MISSING+=("'Address'")
fi
if [ -z "$FORM_title" ]; then
    MISSING+=("'Title'")

fi
if ((${#MISSING[@]} > 0)); then
    export MISSING
    . ./index.cgi
    exit
fi

TAGS=()
if [ -n "$FORM_tags" ]; then
    IFS=',' read -ra TAGS <<< "$FORM_tags"
fi

common_header

echo "<pre>"
if [ -n "$FORM_id" ]; then
    # existing id - do an update
    # TODO
    # $MYSQL << EOF
    echo "<div class=${QQ}error${QQ}>I haven't implemented updates yet, sorry.</div>"
    EOF
else
    # no id - do an insert
    {
        TAG_INSERTS=""
        for tag in "${TAGS[@]}"; do
            tag=$(sed -e "s/^[[:space:]]*//; s/[[:space:]]$//; s/'/''/g" <<< "$tag")
            TAG_INSERTS="${TAG_INSERTS}
SET @tag = '${tag}'; EXECUTE insertTag USING @newId, @tag;"
        done

        # escape '
        SQL_description=$(sed -e "s/'/''/g" <<< "$FORM_description")
        SQL_title=$(sed -e "s/'/''/g" <<< "$FORM_title")

        $MYSQL 2>&1 << EOF
PREPARE insertStmt from 'INSERT INTO sc_bookmarks(bAddress, bDescription, bHash, bStatus, bTitle, uId, bDatetime, bModified) SELECT ?, ?, md5(?), 0, ?, u.uId, now(), now() FROM sc_users u WHERE u.username = ?';
SET @address = '$FORM_address';
SET @description = '$SQL_description';
SET @title = '$SQL_title';
SET @username = '$REMOTE_USER';
EXECUTE insertStmt USING @address, @description, @address, @title, @username;
SELECT @newId := LAST_INSERT_ID();
PREPARE insertTag from 'INSERT INTO sc_tags(bId, tag) VALUES (?, ?)';
${TAG_INSERTS}
EOF
    }
fi

status="$?"

echo "</pre>"

if [ "$status" = "0" ]; then
    cat << EOF
<div class="card">
<h2>Saved Successfully</h2>
<ul>
<li>Go to <a href="/ghettolinks/">Links home page</a>.</li>
<li>Go back to <a href="${FORM_address}">${FORM_title}</a>.</li>
</ul>
</div>
EOF
else
    cat << EOF
<div class="card">
<h2>Save failed for some reason</h2>
<div>Maybe there's some error output above. 😳</div>
</div>
EOF
fi

common_footer
