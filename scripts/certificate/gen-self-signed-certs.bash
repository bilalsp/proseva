#!/bin/bash
# -----------------------------------------------------------------------------
# Generates a self-signed SSL certificate for the ProSeva system.
#
# Reference: https://stackoverflow.com/questions/10175812/how-can-i-generate-a-self-signed-ssl-certificate-using-openssl
# Usage:
#   bash scripts/certificate/gen-self-signed-certs.bash
# -----------------------------------------------------------------------------

SSL_DIR="configs/nginx/ssl"
KEY_FILE="$SSL_DIR/proseva.key"
CRT_FILE="$SSL_DIR/proseva.crt"
CONF_FILE="scripts/certificate/san.cnf"

# Create SSL directory if it does not exist
mkdir -p "$SSL_DIR"

# Generate the self-signed certificate and private key
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout "$KEY_FILE" \
  -out "$CRT_FILE" \
  -config "$CONF_FILE"

echo "Self-signed certificate and key generated:"
echo "  Certificate: $CRT_FILE"
echo "  Key: $KEY_FILE"
