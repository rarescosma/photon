PROJECT=photon
ENTRYPOINT=$(PROJECT).py
PREFIX?=$(HOME)
BINDIR=$(PREFIX)/bin

all: dist/$(PROJECT)

dist/$(PROJECT): .venv/freeze test
	. .venv/bin/activate && pyinstaller --onefile $(ENTRYPOINT)

install: dist/$(PROJECT)
	mkdir -p $(DESTDIR)$(BINDIR)
	cp -f dist/$(PROJECT) $(DESTDIR)$(BINDIR)/
	chmod 755 $(DESTDIR)$(BINDIR)/$(PROJECT)

clean:
	rm -rf dist build *.spec __pycache__ *.egg-info .python-version .venv

test: .venv/freeze
	. .venv/bin/activate && mypy $(PROJECT).py && pylint $(PROJECT).py

.python-version:
	pyenv local 3.7.2

.venv/freeze: .python-version
	test -f .venv/bin/activate || python3 -mvenv .venv --prompt $(PROJECT)
	. .venv/bin/activate \
	  && pip install -e . \
	  && pip install -r test-requirements.txt \
	  && pip freeze > .venv/freeze
