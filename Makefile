VIRTUALENV=virtualenv
VENV=.
PYTHON=$(VENV)/bin/python
DEV_STAMP=.dev_env_installed.stamp
INSTALL_STAMP=.install.stamp

.IGNORE: clean
.PHONY: all install virtualenv tests

OBJECTS = bin/ lib/ local/ include/ man/ .coverage d2to1-0.2.7-py2.7.egg \
	.coverage daybed.egg-info

all: install
install: $(INSTALL_STAMP)
$(INSTALL_STAMP): $(PYTHON)
	$(PYTHON) setup.py develop
	touch $(INSTALL_STAMP)

install-dev: $(DEV_STAMP)
$(DEV_STAMP): $(PYTHON)
	$(VENV)/bin/pip install -r dev-requirements.txt
	touch $(DEV_STAMP)

virtualenv: $(PYTHON)
$(PYTHON):
	$(VIRTUALENV) $(VENV)

clean:
	rm -fr $(OBJECTS) $(DEV_STAMP) $(INSTALL_STAMP)

tests: install-dev
	bin/tox

tests-failfast: .tox/py27/
	.tox/py27/bin/nosetests --with-coverage --cover-package=daybed -x -s

serve: install install-dev
	$(VENV)/bin/pserve development.ini --reload
