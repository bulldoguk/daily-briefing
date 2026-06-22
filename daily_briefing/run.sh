#!/usr/bin/with-contenv bashio

export HA_URL=$(bashio::config 'ha_url')
export HA_TOKEN=$(bashio::config 'ha_token')
export TODO_ENTITY=$(bashio::config 'todo_entity')
export REFRESH_TIME=$(bashio::config 'refresh_time')
export PEOPLE_JSON=$(bashio::config 'people')

export DATA_DIR=/share/daily_briefing
mkdir -p "${DATA_DIR}"

bashio::log.info "Starting Daily Briefing — refresh at ${REFRESH_TIME} daily"

# Force Python to flush stdout immediately so logs show up in the HA log viewer
export PYTHONUNBUFFERED=1

exec python3 /app/entrypoint.py
