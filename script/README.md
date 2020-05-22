# Setup scripts

See <https://github.com/github/scripts-to-rule-them-all>

My interpretation is that `bootstrap` can do the necessary setup. Mostly.
There's not much to this project.

## Manual setup

These things need setting up manually at the moment:

### Apache

This is what the Apache config looks like:

```apache
Alias "/ghettolinks" "path/to/ghettolinks/public"
<Directory "path/to/ghettolinks/public">
Options +ExecCGI
AddHandler cgi-script .cgi
Require all granted
</Directory>
</VirtualHost>
```

Copy to your Apache config, and edit to the correct path.

### Mysql

The `bootstrap` script creates an example `.mysql.cnf` file. Edit it to have the
correct database settings.
