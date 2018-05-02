.PHONY: build-cyberpandas all

all: build-cyberpandas

build-cyberpandas-%:
	LDFLAGS="-headerpad_max_install_name" conda build conda-recipes/cyberpandas $(patsubst build-cyberpandas-%,--python=%,$@)
