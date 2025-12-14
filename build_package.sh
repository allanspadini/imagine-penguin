#!/bin/bash
set -e

# Make sure scripts are executable
chmod +x scripts/postinst.sh scripts/postrm.sh

# Build the package
fpm -s dir -t deb \
    -n imagine-penguin \
    -v 1.0.1 \
    --description "Imagine Penguin is a powerful and intuitive image editing application built with Python and CustomTkinter. It combines classic image processing tools with advanced AI capabilities to help you create, edit, and analyze images with ease." \
    --category utils \
    --architecture amd64 \
    --after-install scripts/postinst.sh \
    --after-remove scripts/postrm.sh \
    --force \
    -C pkg .
