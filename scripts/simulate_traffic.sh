#!/bin/bash

# Simulate random user creation and updates with weighted choice

# Usage: ./simulate_user_activity.sh <delay_in_seconds> <duration_in_seconds>
# Example: ./simulate_user_activity.sh 2 60

DELAY_SECONDS=$1
DURATION_SECONDS=$2

if [[ -z "$DELAY_SECONDS" || -z "$DURATION_SECONDS" ]]; then
  echo "Usage: $0 <delay_in_seconds> <duration_in_seconds>"
  exit 1
fi

START_TIME=$(date +%s)
END_TIME=$((START_TIME + DURATION_SECONDS))

# 0-79 = create, 80-99 = update (80% / 20% split)
while [[ $(date +%s) -lt $END_TIME ]]; do
  CHOICE=$((RANDOM % 100))

  if [[ $CHOICE -lt 80 ]]; then
    echo "🚀 Running: create_users.py --count 1"
    python create_users.py --count 1
  else
    echo "🔄 Running: update_user_email.py --count 1"
    python update_user_email.py --count 1
  fi

  echo "⏳ Waiting $DELAY_SECONDS seconds..."
  sleep "$DELAY_SECONDS"
done

echo "✅ Done! Script ran for $DURATION_SECONDS seconds."
