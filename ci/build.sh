set -e

echo "Building pandas"
conda build conda-recipes/pandas --python ${PYTHON}

echo "Building pandas-ip"
conda build conda-recipes/pandas_ip --python ${PYTHON}
