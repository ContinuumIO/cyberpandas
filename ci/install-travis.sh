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

echo
echo "[install dependencies]"

conda create -q -n test-environment python=${PYTHON}
source activate test-environment

conda install \
      coverage \
      cython \
      flake8 \
      hypothesis \
      numpy \
      pytest \
      pytest-cov \
      python-dateutil \
      pytz \
      six

conda install -c conda-forge pandas>=0.23.0

if [ "${PYTHON}" == "2.7" ]; then
    conda install -q ipaddress
fi

conda list test-environment


# Seeing some failures during conda build like
# error: [Errno 11] write could not complete without blocking
# Apparently, this should fix the problem
# See
# https://github.com/travis-ci/travis-ci/issues/4704
# https://github.com/travis-ci/travis-ci/issues/4704#issuecomment-3484359
# https://github.com/travis-ci/travis-ci/issues/8902
# https://github.com/conda/conda/issues/6473
# https://github.com/conda/conda/issues/6481
# https://github.com/conda/conda/issues/6487

python -c 'import os,sys,fcntl; flags = fcntl.fcntl(sys.stdout, fcntl.F_GETFL); fcntl.fcntl(sys.stdout, fcntl.F_SETFL, flags&~os.O_NONBLOCK);'

echo
echo "[install cyberpandas]"
pip install --no-deps -e .

echo "[finished install]"
conda list

exit 0
