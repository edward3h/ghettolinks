#!/bin/bash

# cgibashopts is an external library which doesn't meet shellcheck requirements
# shellcheck disable=SC1091
. libs/cgibashopts/cgibashopts

# shellcheck source=common.bash
. common.bash

QUERY="SELECT bAddress, bTitle, bDescription, username, 
GROUP_CONCAT(DISTINCT t.tag ORDER by t.tag) as tags, DATE_FORMAT(bDatetime, \'%Y-%m-%d\') as bDate
FROM sc_bookmarks b
JOIN sc_users u USING (uId)
LEFT JOIN (SELECT bId, tag FROM sc_tags WHERE tag NOT LIKE \'system:%\') t USING (bId)
LEFT JOIN sc_tags ts USING (bId)
WHERE (? IS NULL OR username = ?)
AND (? IS NULL OR ts.tag = ?)
AND (? IS NULL OR CONCAT_WS(\'|\', bTitle, bDescription) LIKE ?)
GROUP BY 1,2,3,4,6
ORDER BY bDatetime desc
LIMIT 20;"

USER="NULL";
TAG="NULL";
SEARCH="NULL";

# FORM_ variables are set by cgibashopts
# shellcheck disable=SC2154
if [ -n "$FORM_user" ]; then
    USER="'${FORM_user}'"
fi
# shellcheck disable=SC2154
if [ -n "$FORM_tag" ]; then
    TAG="'${FORM_tag}'"
fi
# shellcheck disable=SC2154
if [ -n "$FORM_search" ]; then
    SEARCH="'%${FORM_search}%'"
fi

EXECUTE_QUERY="PREPARE stmt1 FROM '$QUERY';
SET @username = $USER;
SET @tag = $TAG;
SET @search = $SEARCH;
EXECUTE stmt1 USING @username, @username, @tag, @tag, @search, @search;"


echo "Content-type: text/html"
echo

cat <<EOH
<html>
<head>
<title>Links, interim version</title>
<link rel="stylesheet" type="text/css" href="index.css">
</head>
<body><header><h1>Links</h1></header>
<section id="links">
EOH

$MYSQL -e "$EXECUTE_QUERY" | sed 's/\t\t/\t@NULL@\t/g' | while IFS=$'\t' read -r address title description username tags bDate; do
if [ "$description" = "@NULL@" ]; then
    description=""
fi
cat <<EOF
    <div class="card">
    <div class="link"><a href="$address">$title</a></div>
    <div class="description">$description</div>
    <div class="info">
    <div class="infoLabel">User</div>
    <div class="username">$username</div>
    <div class="infoLabel">Tags</div>
    <div class="tags">$tags</div>
    <div class="infoLabel">Bookmarked</div>
    <div class="date">$bDate</div>
    </div>
    </div>
EOF
done


cat <<EOF
</section>
</body>
</html>
EOF