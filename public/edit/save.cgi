#!/bin/bash
# shellcheck disable=SC2154

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
echo "TAGS " "${TAGS[@]}"
if [ -n "$FORM_id" ]; then
    # existing id - do an update
    # TODO
    $MYSQL << EOF
EOF
else
    # no id - do an insert
    {
        TAG_INSERTS=""
        for tag in "${TAGS[@]}"; do
            tag=$(sed -e 's/^[[:space:]]*//; s/[[:space:]]$//' <<< "$tag")
            TAG_INSERTS="${TAG_INSERTS}
SET @tag = '${tag}'; EXECUTE insertTag USING @newId, @tag;"
        done
        echo "TAG_INSERTS ${TAG_INSERTS}"

        $MYSQL 2>&1 << EOF
PREPARE insertStmt from 'INSERT INTO sc_bookmarks(bAddress, bDescription, bHash, bStatus, bTitle, uId, bDatetime, bModified) SELECT ?, ?, md5(?), 0, ?, u.uId, now(), now() FROM sc_users u WHERE u.username = ?';
SET @address = '$FORM_address';
SET @description = '$FORM_description';
SET @title = '$FORM_title';
SET @username = '$REMOTE_USER';
EXECUTE insertStmt USING @address, @description, @address, @title, @username;
SELECT @newId := LAST_INSERT_ID();
PREPARE insertTag from 'INSERT INTO sc_tags(bId, tag) VALUES (?, ?)';
${TAG_INSERTS}
EOF
    }
fi

echo "$?"

echo "</pre>"

common_footer
