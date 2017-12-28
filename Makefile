.PHONY: build-pandas build-pandas-pandas-ip all

all: build-pandas build-pandas-ip

build-pandas:
	conda build conda-recipes/pandas

build-pandas-ip:
	conda build conda-recipes/pandas_ip
