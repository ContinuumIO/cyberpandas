.PHONY: build-pandas build-pandas-pandas-ip all

all: build-pandas build-pandas-ip

build-pandas:
	LDFLAGS="-headerpad_max_install_name" conda build conda-recipes/pandas

build-pandas-ip:
	LDFLAGS="-headerpad_max_install_name" conda build conda-recipes/pandas_ip
