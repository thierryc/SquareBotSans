PYTHON ?= $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)
FONTBAKERY ?= $(shell if [ -x .venv/bin/fontbakery ]; then echo .venv/bin/fontbakery; else echo fontbakery; fi)

.PHONY: build test test-googlefonts test-googlefonts-local test-universal

build:
	$(PYTHON) tools/build_distribution_fonts.py

test: test-universal test-googlefonts

test-googlefonts: build
	$(FONTBAKERY) check-googlefonts --skip-network build/googlefonts/squarebotsans/*.ttf

test-googlefonts-local: build
	$(FONTBAKERY) check-googlefonts --skip-network -x googlefonts/family_name_compliance build/googlefonts/squarebotsans/*.ttf

test-universal:
	$(FONTBAKERY) check-universal --skip-network fonts/otf/*.otf fonts/variable/*.ttf fonts/googlefonts/*.ttf
