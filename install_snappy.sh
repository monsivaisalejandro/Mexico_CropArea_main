#!/bin/bash
set -e

# 1. Environment Detection
REAL_USER=${SUDO_USER:-$(whoami)}
REAL_HOME=$(getent passwd "$REAL_USER" | cut -d: -f6)
SNAP_DEST="/opt/snap"

# Get current Conda environment paths
CONDA_PYTHON=$(which python)
CONDA_SITE=$(python -c "import site; print(site.getsitepackages()[0])")

echo "### 1. System Dependencies ###"
apt-get update
apt-get install -y wget curl unzip libgfortran5 libgomp1 default-jdk \
    python3 python3-pip python3-dev build-essential libgdal-dev

echo "### 2. Installing SNAP 13 ###"
if [ ! -f "esa-snap_all_linux-13.0.0.sh" ]; then
    wget https://download.esa.int/step/snap/13.0/installers/esa-snap_all_linux-13.0.0.sh
fi
chmod +x esa-snap_all_linux-13.0.0.sh
./esa-snap_all_linux-13.0.0.sh -q -dir "$SNAP_DEST"
rm esa-snap_all_linux-13.0.0.sh
chown -R $REAL_USER:$REAL_USER "$SNAP_DEST"

# Update SNAP modules
"$SNAP_DEST/bin/snap" --nosplash --nogui --modules --update-all || true

echo "### 3. Conda Environment Setup ###"
# Force install esa-snappy shim into the Conda site-packages
# This prevents the 'package does not exist' error in snappy-conf
$CONDA_PYTHON -m pip install esa-snappy jpy numpy matplotlib --target "$CONDA_SITE" --upgrade

echo "### 4. Configuring snappy-conf for Conda ###"
# Run the configuration tool pointing directly to the Conda env
"$SNAP_DEST/bin/snappy-conf" "$CONDA_PYTHON" "$CONDA_SITE"

# Increase Java Memory for the bridge (crucial for satellite data)
# Default is usually 512m; bumping to 8G
if [ -f "$CONDA_SITE/esa_snappy/snappy.ini" ]; then
    sed -i 's/-Xmx512m/-Xmx8G/g' "$CONDA_SITE/esa_snappy/snappy.ini"
fi

# Update .bashrc for persistence
if ! grep -q "SNAP_HOME" "$REAL_HOME/.bashrc"; then
    cat <<EOF >> "$REAL_HOME/.bashrc"
# SNAP Configuration
export SNAP_HOME=$SNAP_DEST
export PATH=\$PATH:\$SNAP_HOME/bin
EOF
fi

echo "---"
echo "Done! SNAP 13 and the Python bridge (esa_snappy) are configured for your Conda env."
echo "Test it with: python -c 'import esa_snappy; print(\"Success!\")'"
echo "Please run: source ~/.bashrc"
