#!/usr/bin/env -S bash --login
set -euo pipefail

basedir=$(dirname "$(readlink -f "$0")")
rootdir=$(dirname "$basedir")

# ✅ DPS runs from the job working dir, input/ is relative to that
WORKING_DIR=$(pwd)
mkdir -p "${WORKING_DIR}/output/"
INPUT_DIR="${WORKING_DIR}/input"

echo "Working dir: $WORKING_DIR"
echo "Looking for input in: $INPUT_DIR"
ls -la "$INPUT_DIR" || echo "⚠️ input dir contents above"

mkdir -p "${WORKING_DIR}/output"

# Find the product
input_product=$(find "$INPUT_DIR" -maxdepth 1 -name "*.zip" -o -name "*.SAFE" | head -n 1)

if [ -z "$input_product" ]; then
    echo "❌ Error: No Sentinel-1 product (.zip or .SAFE) found in input directory."
    ls -la "$INPUT_DIR" || echo "(directory not found)"
    exit 1
fi

input_product=$(realpath "$input_product")

echo "Using input product: $input_product"
echo "File exists: $(test -f "$input_product" && echo YES || echo NO)"

wkt_roi=${1:-"POLYGON((-98.06 19.5, -97.5 19.5, -97.5 19.28, -98.06 19.28, -98.06 19.5))"}
output_name=${2:-"processed_result.tif"}

echo "ROI: $wkt_roi"
echo "Output name: $output_name"

export PYTHONPATH="${PYTHONPATH:-}:${rootdir}"

cd "$rootdir"

conda run --live-stream --name python python ${basedir}/process_sentinel1.py \
    --product_path "$input_product" \
    --wkt_roi "$wkt_roi" \
    --output_file "${WORKING_DIR}/output/$output_name"
