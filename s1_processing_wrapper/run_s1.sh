#!/usr/bin/env -S bash --login
set -euo pipefail

basedir=$(dirname "$(readlink -f "$0")")

# Create output directory for DPS
mkdir -p output

# DPS downloads all files provided as inputs into 'input'
INPUT_DIR=input

# Debug: show what DPS actually staged
echo "=== Contents of ${INPUT_DIR}/ ==="
ls -la "$INPUT_DIR" || echo "(input dir missing or empty)"
find "$INPUT_DIR" -maxdepth 3 -print
echo "=================================="

# Find the input product: match .zip or .SAFE, case-insensitive,
# search up to 2 levels deep in case DPS nests it in a subfolder
input_product=$(find "$INPUT_DIR" -maxdepth 2 \( -iname "*.zip" -o -iname "*.safe" \) | head -n 1)

if [ -z "$input_product" ]; then
  echo "❌ Error: No Sentinel-1 product (.zip or .SAFE) found in input directory."
  echo "Available files were listed above — check naming/extension/nesting."
  exit 1
fi


# Convert to absolute path before changing directories
input_product=$(readlink -f "$input_product")

echo "Using input product: $input_product"
echo "File exists: $(test -e "$input_product" && echo YES || echo NO)"

wkt_roi=${1:-"POLYGON((-98.06 19.5, -97.5 19.5, -97.5 19.28, -98.06 19.28, -98.06 19.5))"}
output_name=${2:-"processed_result.tif"}

echo "ROI: $wkt_roi"
echo "Output name: $output_name"

output_dir=$(readlink -f output)

export PYTHONPATH="$(dirname "$basedir"):${PYTHONPATH:-}"
conda run --live-stream --name python python ${basedir}/process_sentinel1.py \
    --product_path "$input_product" \
    --wkt_roi "$wkt_roi" \
    --output_file "${output_dir}/${output_name}"
