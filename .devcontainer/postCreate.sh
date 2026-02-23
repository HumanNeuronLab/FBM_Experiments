#!/usr/bin/env bash
set -euo pipefail

# System deps for building older Python + common scientific/GUI libs
sudo apt-get update
sudo apt-get install -y \
  build-essential curl git \
  zlib1g-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev \
  libffi-dev liblzma-dev tk-dev \
  libglib2.0-0 libsm6 libxext6 libxrender1 \
  portaudio19-dev

# Install pyenv
if [ ! -d "$HOME/.pyenv" ]; then
  curl https://pyenv.run | bash
fi

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Install Python 3.6 (pin patch version for reproducibility)
pyenv install -s 3.6.15
pyenv local 3.6.15

# Create venv for the project
python -m venv .venv
source .venv/bin/activate

# Older Python needs older pip/setuptools ranges to avoid breakage
python -m pip install --upgrade "pip<22" "setuptools<60" "wheel<0.38"

# Install your dependencies
python -m pip install -r requirements.txt

# Quick import sanity check (fast fail if deps are broken)
python -c "import psychopy; import numpy; import pandas; print('Codespaces imports OK')"
