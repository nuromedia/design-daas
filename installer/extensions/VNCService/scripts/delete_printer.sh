#!/bin/sh

NAME="$1"

# Delete printer, config file, log file and output folder
if lpstat -p "$NAME"; then
    lpadmin -x "$NAME"
    rm -r "/usr/src/app/files/$NAME"
    rm "/etc/cups/cups-pdf-$NAME.conf"
    rm "/var/log/cups/cups-pdf-${NAME}_log"
else
    echo "Printer $NAME does not exist."
fi

return 0