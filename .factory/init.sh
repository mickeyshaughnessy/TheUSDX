#!/bin/bash
set -e

cd /Users/michaelshaughnessy/Repos/TheUSDX

# Install dependencies if needed
pip3 install -r requirements.txt 2>/dev/null || true

echo "USDX environment ready"
