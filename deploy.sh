#!/usr/bin/env bash

set -euo pipefail

# Pull in local variables (not committed)
if [ -f .env ]; then
    source .env
fi

sam deploy --parameter-overrides AllowedIpAddress="$ALLOWED_IP_ADDRESS"
