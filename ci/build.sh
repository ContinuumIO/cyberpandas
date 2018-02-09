set -e
echo "Building cyberpandas"

conda build conda-recipes/cyberpandas --python ${PYTHON}
