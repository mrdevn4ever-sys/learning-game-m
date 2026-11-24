#!/usr/bin/env bash
set -euo pipefail
export DEVELOPER_DIR=/Applications/Xcode_27.2.app/Contents/Developer
# Unsigned diagnosis only; build and xcresult stay in RUNNER_TEMP.
python produkt/werkzeuge/ci/native_run.py
