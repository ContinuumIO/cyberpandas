set -e
echo "Building pandas-ip"

conda build conda-recipes/pandas_ip --python ${PYTHON}
