# 'library' file

MYSQL="mysql --defaults-extra-file=.mysql.cnf --skip-column-names --batch"
export MYSQL

function common_header {
echo "Content-type: text/html"
echo

cat <<EOH
<html>
<head>
<title>Links, interim version</title>
<link rel="stylesheet" type="text/css" href="index.css">
</head>
<body><header><h1>Links</h1><img src="HeHeartlandEstates4894iconsconstruction.gif" width="574" height="51"></header>
<div id="content">
EOH
}

function common_footer {
cat <<EOF
</div>
</body>
</html>
EOF
}

function error_response {
    STATUS="500 Server Error"
    MESSAGE="Something is wrong, but I haven't implemented good error handling on this service yet, sorry."
    if [ -n "$1" ]; then
        STATUS="$1"
    fi
    if [ -n "$2" ]; then
        MESSAGE="$2"
    fi
    echo "Status: $STATUS"
    common_header
cat <<EOF
<div class="error">
<h2>$STATUS</h2>
<div>$MESSAGE</div>
</div>
EOF
    common_footer
    exit 0
}