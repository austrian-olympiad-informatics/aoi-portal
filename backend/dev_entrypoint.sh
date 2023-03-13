#!/bin/bash

set -euxo pipefail

pip3 install -e .
exec aoiportal -c /config.yaml run --host 0.0.0.0 --port 5000
