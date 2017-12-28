#!/bin/bash
set -e
echo "[install-travis]"

# install iniconda
MINICONDA_DIR="$HOME/miniconda3"
time wget -q http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh || exit 1
time bash miniconda.sh -b -p "$MINICONDA_DIR" || exit 1

echo
echo "[show conda]"
which conda

echo
echo "[update conda]"
conda config --set always_yes true --set changeps1 false || exit 1
conda update -q conda

echo
echo "[conda build]"
conda install -q conda-build anaconda-client --yes

# echo
# echo "[add channels]"
# conda config --add channels conda-forge || exit 1

conda create -q -n test-environment python=${PYTHON}
source activate test-environment

conda install -q \
      coverage \
      cython \
      flake8 \
      numpy \
      pytest \
      pytest-cov \
      python-dateutil \
      pytz \
      six

conda list test-environment


echo
echo "[building pandas]"
conda build -q conda-recipes/pandas --python=${PYTHON}

echo "[installing pandas]"
conda install -q $(conda build conda-recipes/pandas --python=${PYTHON} --output)

echo
echo "[install pandas-ip]"
pip install -e .

exit 0
