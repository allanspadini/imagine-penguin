#!/bin/sh
set -e

if [ "$1" = "configure" ]; then
    update-desktop-database >/dev/null 2>&1 || true
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor >/dev/null 2>&1 || true
fi
