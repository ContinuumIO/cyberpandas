set -e
echo "Building pandas-ip"

pwd

ls
ls conda-recipes

conda build conda-recipes/pandas_ip --python ${PYTHON}
