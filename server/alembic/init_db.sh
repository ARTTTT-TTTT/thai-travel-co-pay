#! /usr/bin/env bash

# * chmod +x ./alembic/init_db.sh
# * ./alembic/init_db.sh

set -e
set -x

python app/database/init_db.py

# alembic upgrade head
