#!/bin/bash

# -----------------------------------------------------------------------------
# Script: add_hosts_entries.sh
#
# Description:
#   Adds specified hostname entries to the system's hosts file if they
#   don't already exist.
#
# Usage:
#   - Run VSCode or terminal as Administrator/root.
#   - Execute: bash scripts/add_hosts_entries.sh
# -----------------------------------------------------------------------------

# Detect OS and set hosts file path accordingly
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
  HOSTS_FILE="/c/Windows/System32/drivers/etc/hosts"
else
  HOSTS_FILE="/etc/hosts"
fi

# List of host entries to add
ENTRIES=(
  "127.0.0.1 api-listing.proseva.net"
  "127.0.0.1 keycloak.proseva.net"
)

add_host_entry() {
  local entry="$1"
  if grep -Fxq "$entry" "$HOSTS_FILE"; then
    echo "Entry already exists: $entry"
  else
    echo "Adding entry: $entry"
    echo "$entry" >> "$HOSTS_FILE"
  fi
}

for entry in "${ENTRIES[@]}"; do
  add_host_entry "$entry"
done
