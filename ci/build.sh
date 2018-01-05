set -e
echo "Building pandas-ip"

pwd

echo "ls -lha"
ls -lha
ls conda-recipes/pandas_ip

conda build conda-recipes/pandas_ip --python ${PYTHON}
conda build conda-recipes/pandas --python ${PYTHON}
