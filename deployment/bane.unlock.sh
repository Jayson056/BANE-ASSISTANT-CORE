#!/bin/bash
# BANE - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
# BANE Core Unlocking Script


echo "🔓 BANE: Entering Maintenance Mode"

BANE_CORE="/home/son/BANE"

sudo chown -R son:son "$BANE_CORE"
sudo chmod -R 775 "$BANE_CORE"

# Create maintenance flag file
touch "$BANE_CORE/.maintenance"

echo "✅ Core unlocked for maintenance/upgrades."
echo "⚠️  Remember to run 'bane.lock.sh' when finished!"
