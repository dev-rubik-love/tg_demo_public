#!/bin/bash

sudo chmod +x ./db_setup.sh && ./db_setup.sh || true  # True to run next line anyway
source venv/bin/activate && python -m app
