#!/usr/bin/env bash
set -e
echo "Building cyberpandas"

conda build -c defaults -c conda-forge/label/rc conda-recipes/cyberpandas --python=${PYTHON}
