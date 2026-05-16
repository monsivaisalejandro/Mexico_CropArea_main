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

# Find the first file in input (the zip product or SAFE directory)
input_product=$(find input -maxdepth 1 -name "*.zip" -o -name "*.SAFE" | head -n 1)

if [ -z "$input_product" ]; then
    echo "❌ Error: No Sentinel-1 product (.zip or .SAFE) found in input directory."
    exit 1
fi

# Convert to absolute path before changing directories
input_product=$(readlink -f "$input_product")

echo "Using input product: $input_product"

# Read the positional arguments (WKT ROI and output filename)
wkt_roi=${1:-"POLYGON((-98.06 19.5, -97.5 19.5, -97.5 19.28, -98.06 19.28, -98.06 19.5))"}
output_name=${2:-"processed_result.tif"}

echo "ROI: $wkt_roi"
echo "Output name: $output_name"

# Add the root directory to PYTHONPATH so local modules can be found
export PYTHONPATH="${PYTHONPATH:-}:${rootdir}"

# Call process_sentinel1.py from the root directory
cd "$rootdir"
conda run --live-stream --name python python ${basedir}/process_sentinel1.py \
    --product_path "$input_product" \
    --wkt_roi "$wkt_roi" \
    --output_file "output/$output_name"
