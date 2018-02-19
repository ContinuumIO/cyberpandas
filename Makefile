.PHONY: build-pandas build-pandas build-cyberpandas all

all: build-pandas build-cyberpandas

build-pandas-2.7:
	LDFLAGS="-headerpad_max_install_name" conda build conda-recipes/pandas --python=2.7 --numpy=1.9

build-pandas-3.5:
	LDFLAGS="-headerpad_max_install_name" conda build conda-recipes/pandas --python=3.5 --numpy=1.9

build-pandas-3.6:
	LDFLAGS="-headerpad_max_install_name" conda build conda-recipes/pandas --python=3.6 --numpy=1.11

build-cyberpandas-%:
	LDFLAGS="-headerpad_max_install_name" conda build conda-recipes/cyberpandas $(patsubst build-cyberpandas-%,--python=%,$@)
