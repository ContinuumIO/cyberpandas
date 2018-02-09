.PHONY: build-pandas build-pandas build-cyberpandas all

all: build-pandas build-cyberpandas

build-pandas:
	LDFLAGS="-headerpad_max_install_name" conda build conda-recipes/pandas

build-cyberpandas:
	LDFLAGS="-headerpad_max_install_name" conda build conda-recipes/cyberpandas
