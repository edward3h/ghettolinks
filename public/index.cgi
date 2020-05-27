#!/bin/bash

# Main page - render list of bookmarks/links

# shellcheck disable=SC1091
. ../common.bash

QUERY="SELECT bAddress, bTitle, bDescription, username,
GROUP_CONCAT(DISTINCT t.tag ORDER by t.tag SEPARATOR \', \') as tags, DATE_FORMAT(bDatetime, \'%Y-%m-%d\') as bDate,
MATCH(bTitle, bDescription) AGAINST (?) as relevance, bFavicon, bId
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

USER="NULL"
TAG="NULL"
SEARCH="NULL"

# FORM_ variables are set by cgibashopts
# shellcheck disable=SC2154
if [ -n "$FORM_user" ]; then
    USER="'${FORM_user}'"
    USERVAL=$(sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g; s/'"'"'/\&#39;/g' <<< "$FORM_user")
fi
# shellcheck disable=SC2154
if [ -n "$FORM_tag" ]; then
    TAG="'${FORM_tag}'"
    TAGVAL=$(sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g; s/'"'"'/\&#39;/g' <<< "$FORM_tag")
fi
# shellcheck disable=SC2154
if [ -n "$FORM_search" ]; then
    SEARCH="'${FORM_search}'"
    SEARCHVAL=$(sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g; s/'"'"'/\&#39;/g' <<< "$FORM_search")
fi

EXECUTE_QUERY="PREPARE stmt1 FROM '$QUERY';
SET @username = $USER;
SET @tag = $TAG;
SET @search = $SEARCH;
EXECUTE stmt1 USING @search, @username, @username, @tag, @tag, @search, @search;"

common_header

cat << EOH
<nav id="params">
<form method="GET" action="">
<div class="search">
<h3>Search</h3>
<input type="text" name="search" value="$SEARCHVAL">
<input type="submit" value="Search">
<input type="hidden" name="tag" value="$TAGVAL">
</div>
EOH
if [ -n "$REMOTE_USER" ]; then
    cat << EOH
<div class="search">
<h3>User</h3>
<input id="user_all" type="radio" name="user" value=""><label for="user_all">All links</label>
<input id="user_me" type="radio" name="user" value="${REMOTE_USER}"><label for="user_me">My links</label>
</div>
EOH
else
    cat << EOH
<input type="hidden" name="user" value="$USERVAL">
EOH
fi
cat << EOH
</form>
<div class="card">
<h3>Adding Bookmarks</h3>
Drag this bookmarklet link to your bookmark bar:
<a href="javascript:location.href='http://192.168.164.146/ghettolinks/edit/?v=4;address='+encodeURIComponent(location.href)+';title='+encodeURIComponent(document.title)">Bookmark This</a>
When you're on a page you want to bookmark, click the bookmarklet.
</div>
</nav>
<section id="links">
EOH

# shellcheck disable=SC2034
$MYSQL -e "$EXECUTE_QUERY" | sed 's/\t\t/\t@NULL@\t/g' | while IFS=$'\t' read -r address title description username tags bDate relevance favicon id; do
    if [ "$description" = "@NULL@" ]; then
        description=""
    fi
    if [ -f "favicons/$favicon" ]; then
        FIIMAGE="<img class=${QQ}favicon${QQ} src=${QQ}favicons/$favicon${QQ}>"
    else
        FIIMAGE="<span class=${QQ}favicon${QQ}>🔗</span> "
    fi
    if [ -f "thumbnails/${id}.png" ]; then
        THIMAGE="<img src=${QQ}thumbnails/${id}.png${QQ}>"
    else
        THIMAGE=""
    fi
    cat << EOF
    <div class="card">
    <div class="link"><a href="$address">${FIIMAGE}<span>$title</span></a></div>
    <div class="description">$description</div>

    <div class="info infoLabel">User</div>
    <div class="info username">$username</div>
    <div class="info infoLabel">Tags</div>
    <div class="info tags">$tags</div>
    <div class="info infoLabel">Bookmarked</div>
    <div class="info date">$bDate</div>

    <div class="thumbnail"><a href="$address">$THIMAGE</a></div>
    </div>
EOF
done

cat << EOF
</section>
EOF

common_footer
