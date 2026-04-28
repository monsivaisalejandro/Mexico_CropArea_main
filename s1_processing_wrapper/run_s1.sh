#!/usr/bin/env -S bash --login
set -euo pipefail
# This script is the one that is called by the DPS.

# Get current location of build script
basedir=$(dirname "$(readlink -f "$0")")
# Get the root of the repo (one level up)
rootdir=$(dirname "$basedir")

# Create output directory for DPS
mkdir -p output

# DPS downloads all files provided as inputs into 'input'
INPUT_DIR=input

# Find the first file in input (the zip product)
input_product=$(find input -name "*.zip" | head -n 1)

# Read the positional arguments (WKT ROI and output filename)
wkt_roi=$1
output_name=$2

# Call process_sentinel1.py from the root directory
# Note: we need to ensure the python path is set correctly or we are in the root
cd "$rootdir"
conda run --live-stream --name python python process_sentinel1.py "$input_product" "$wkt_roi" "output/$output_name"
