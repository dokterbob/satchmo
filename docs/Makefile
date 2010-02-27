# Makefile for Sphinx documentation
#
# Typical usage for Satchmo:
# make DJANGOSETTINGS=simplestore.settings ROOT_DIR=/path/to/satchmo-working/ html

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
DJANGOSETTINGS =
ROOT_DIR =

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d .build/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help clean sphinx-autodoc html web pickle htmlhelp latex changes linkcheck

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  pickle    to make pickle files (usable by e.g. sphinx-web)"
	@echo "  htmlhelp  to make HTML files and a HTML help project"
	@echo "  latex     to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  changes   to make an overview over all changed/added/deprecated items"
	@echo "  linkcheck to check all external links for integrity"
	@echo ""
	@echo "Ensure also that ROOT_DIR is defined (the absolute path to the directory"
	@echo "containing satchmo's apps and projects, usually the parent directory of"
	@echo "this file)."

clean:
	-rm -rf .build/*

sphinx-autodoc:
#
# Set up a django/satchmo store for sphinx's autodoc.
#

# You *must* set this variable from the command line.
ifeq ($(ROOT_DIR),)
	@echo "Please define ROOT_DIR (the absolute path to the directory containing"
	@echo "satchmo's apps and projects, usually the parent directory of this file)."
	@exit 2
endif

# The separator used in PATH.
# Use ":" unless WINDOWS is defined (use ";" instead).
#
# Indent with space here instead of tabs so that make doesn't treat lines as a
# shell command.
ifdef WINDOWS
PATHSEP = \;
else
PATHSEP = :
endif

# Paths
SATCHMO_APPS = $(ROOT_DIR)/apps
PROJECT_DIR = $(ROOT_DIR)/projects

# Set them in the environment so that the sphinx child process find
# satchmo and friends.
export PYTHONPATH = $(shell echo $$PYTHONPATH)$(PATHSEP)$(SATCHMO_APPS)$(PATHSEP)$(PROJECT_DIR)
export DJANGO_SETTINGS_MODULE = $(DJANGOSETTINGS)

html: sphinx-autodoc
	mkdir -p .build/html .build/doctrees
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) .build/html
	@echo
	@echo "Build finished. The HTML pages are in .build/html."

pickle: sphinx-autodoc
	mkdir -p .build/pickle .build/doctrees
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS) .build/pickle
	@echo
	@echo "Build finished; now you can process the pickle files or run"
	@echo "  sphinx-web .build/pickle"
	@echo "to start the sphinx-web server."

web: pickle

htmlhelp: sphinx-autodoc
	mkdir -p .build/htmlhelp .build/doctrees
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS) .build/htmlhelp
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in .build/htmlhelp."

latex: sphinx-autodoc
	mkdir -p .build/latex .build/doctrees
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) .build/latex
	@echo
	@echo "Build finished; the LaTeX files are in .build/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

changes: sphinx-autodoc
	mkdir -p .build/changes .build/doctrees
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) .build/changes
	@echo
	@echo "The overview file is in .build/changes."

linkcheck: sphinx-autodoc
	mkdir -p .build/linkcheck .build/doctrees
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) .build/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in .build/linkcheck/output.txt."
