#!/bin/bash

set -e
set -u

case $# in
0) pkg="-e git+https://github.com/nxsy/gibe2.git#egg=Gibe2" ;;
*) pkg="$1" ;;
esac


cd `dirname $0`
if [ ! -d .env ]; then
    python scripts/virtualenv.py --no-site-packages --distribute .env
fi
if [ ! -e activate ]; then
    ln -s .env/bin/activate activate
fi

# activate plays fast and loose with variables
set +u
source activate
set -u

pip install ${pkg}

BINS="gibe2"
for bin in ${BINS}; do
    if [ ! -e ${bin} ]; then
        ln -s .env/bin/${bin}
    fi
done

EB_FILES="eb"
for eb_file in ${EB_FILES}; do
    if [ ! -e ${eb_file} ]; then
        ln -s scripts/elastic-beanstalk/${eb_file}
    fi
done

pip install awsebcli feedgenerator
