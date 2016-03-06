#!/bin/sh

set -e
set -u

cd `dirname $0`
cd ..

rm -rf .env
rm -f activate
rm -f gibe2
rm -rf build
rm -rf static/.webassets-cache
rm -f static/cache_*

find . -type f -name "*.pyc" -delete
