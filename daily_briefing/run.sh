#!/usr/bin/with-contenv bashio

export DATA_DIR=/share/daily_briefing
mkdir -p "${DATA_DIR}"

bashio::log.info "Starting Daily Briefing"

# Force Python to flush stdout immediately so logs show up in the HA log viewer
export PYTHONUNBUFFERED=1

exec python3 /app/entrypoint.py
