#!/bin/bash

# Change to the project directory
cd /home/ubuntu/macrogen-assistant || { echo "Directory not found!"; exit 1; }

# Remove remaining chat files
zip_count=$(ls *.zip 2>/dev/null | wc -l)
echo "$(date '+%Y-%m-%d %H:%M:%S') Removing $zip_count chat files..."
rm *.zip
