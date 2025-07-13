#! /usr/bin/env bash

# * chmod +x ./scripts/init_db.sh
# * ./scripts/init_db.sh

set -e
set -x

python app/database/init_db.py
