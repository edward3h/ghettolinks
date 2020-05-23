#!/bin/bash

# Main page - render list of bookmarks/links

# shellcheck disable=SC1091
. ../common.bash

QUERY="SELECT bAddress, bTitle, bDescription, username,
GROUP_CONCAT(DISTINCT t.tag ORDER by t.tag) as tags, DATE_FORMAT(bDatetime, \'%Y-%m-%d\') as bDate,
MATCH(bTitle, bDescription) AGAINST (?) as relevance
FROM sc_bookmarks b
JOIN sc_users u USING (uId)
LEFT JOIN (SELECT bId, tag FROM sc_tags WHERE tag NOT LIKE \'system:%\') t USING (bId)
LEFT JOIN sc_tags ts USING (bId)
WHERE (? IS NULL OR username = ?)
AND (? IS NULL OR ts.tag = ?)
AND (? IS NULL OR MATCH(bTitle, bDescription) AGAINST (?))
GROUP BY 1,2,3,4,6
ORDER BY relevance desc, bDatetime desc
LIMIT 20;"

USER="NULL";
TAG="NULL";
SEARCH="NULL";

# FORM_ variables are set by cgibashopts
# shellcheck disable=SC2154
if [ -n "$FORM_user" ]; then
    USER="'${FORM_user}'"
    USERVAL=$(sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g; s/'"'"'/\&#39;/g' <<<"$FORM_user")
fi
# shellcheck disable=SC2154
if [ -n "$FORM_tag" ]; then
    TAG="'${FORM_tag}'"
    TAGVAL=$(sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g; s/'"'"'/\&#39;/g' <<<"$FORM_tag")
fi
# shellcheck disable=SC2154
if [ -n "$FORM_search" ]; then
    SEARCH="'${FORM_search}'"
    SEARCHVAL=$(sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g; s/'"'"'/\&#39;/g' <<<"$FORM_search")
fi

EXECUTE_QUERY="PREPARE stmt1 FROM '$QUERY';
SET @username = $USER;
SET @tag = $TAG;
SET @search = $SEARCH;
EXECUTE stmt1 USING @search, @username, @username, @tag, @tag, @search, @search;"

common_header

cat <<EOH
<nav id="params">
<form method="GET" action="">
<div class="search">
<input type="text" name="search" value="$SEARCHVAL">
<input type="submit" value="Search">
<input type="hidden" name="user" value="$USERVAL">
<input type="hidden" name="tag" value="$TAGVAL">
</div>
</form>
<div class="card">
Drag this link to your bookmark bar:
<a href="javascript:location.href='http://192.168.164.146/ghettolinks/edit/?v=4;address='+encodeURIComponent(location.href)+';title='+encodeURIComponent(document.title)">Bookmark This</a>
</div>
</nav>
<section id="links">
EOH

# shellcheck disable=SC2034
$MYSQL -e "$EXECUTE_QUERY" | sed 's/\t\t/\t@NULL@\t/g' | while IFS=$'\t' read -r address title description username tags bDate relevance; do
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
EOF

common_footer
