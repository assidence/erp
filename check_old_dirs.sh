#!/bin/bash
echo "=== Checking old directories ==="
for dir in Suppliers Parts MaterialIns ProductOuts; do
    if [ -d "/home/ubuntu/erp/frontend/src/pages/$dir" ]; then
        echo "$dir EXISTS - needs deletion"
    else
        echo "$dir NOT FOUND"
    fi
done

echo ""
echo "=== Current pages directory ==="
ls -la /home/ubuntu/erp/frontend/src/pages/