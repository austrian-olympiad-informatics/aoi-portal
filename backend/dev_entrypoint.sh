#!/bin/bash

set -euo pipefail

pip3 install -e .

# Wait for the database to become available and create any missing tables.
# initdb runs SQLAlchemy's create_all(), which is idempotent, so it is safe to
# run on every startup. We also use it as our database readiness probe.
echo "Waiting for the database and initializing the schema..."
until aoiportal -c /config.yaml initdb; do
  echo "Database not ready yet, retrying in 2s..."
  sleep 2
done

# Bootstrap a default admin account for local development if none exists yet.
# Credentials match the devenv setup: t.rainer@example.org / password1
aoiportal -c /config.yaml addadmin \
  --email t.rainer@example.org \
  --first-name Theodor \
  --last-name Rainer \
  --password password1 \
  --skip-existing

exec aoiportal -c /config.yaml run --host 0.0.0.0 --port 5000
