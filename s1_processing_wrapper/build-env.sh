#!/usr/bin/env -S bash --login
set -euo pipefail
# This script is used to install any custom packages required by the algorithm.

# Get current location of build script
basedir=$( cd "$(dirname "$0")" ; pwd -P )
# Get the root of the repo (one level up)
rootdir=$(dirname "$basedir")

# Create the environment if it doesn't exist, or update it if it does
conda env create -f ${basedir}/environment.yml || conda env update -f ${basedir}/environment.yml

# Capture the exact paths for the 'python' environment
ENV_PYTHON=$(conda run --name python which python)
ENV_SITE=$(conda run --name python python -c "import site; print(site.getsitepackages()[0])")

# Install SNAP and configure the esa_snappy bridge for the 'python' environment
bash ${rootdir}/install_snappy.sh "$ENV_PYTHON" "$ENV_SITE"
