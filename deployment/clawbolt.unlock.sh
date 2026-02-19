#!/bin/bash
# CLAWBOLT - Created by Jayson056
# Copyright (c) 2026 Jayson056. All rights reserved.
# CLAWBOLT Core Unlocking Script


echo "🔓 BANE: Entering Maintenance Mode"

BANE_CORE="/home/user/BANE_CORE"

sudo chown -R son:son "$BANE_CORE"
sudo chmod -R 775 "$BANE_CORE"

# Create maintenance flag file
touch "$BANE_CORE/.maintenance"

echo "✅ Core unlocked for maintenance/upgrades."
echo "⚠️  Remember to run 'clawbolt.lock.sh' when finished!"
