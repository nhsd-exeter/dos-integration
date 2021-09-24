PYTHON_VERSION_MAJOR = 3
PYTHON_VERSION_MINOR = 9
PYTHON_VERSION_PATCH = 5
PYTHON_VERSION = $(PYTHON_VERSION_MAJOR).$(PYTHON_VERSION_MINOR).$(PYTHON_VERSION_PATCH)
PYTHON_BASE_PACKAGES = \
	awscli-local==0.14 \
	awscli==1.19.84 \
	black==21.5b1 \
	boto3==1.17.84 \
	bpython \
	configparser \
	coverage \
	diagrams==0.20.0 \
	flake8 \
	mypy \
	prettytable \
	pygments \
	pylint \
	pyyaml \
	requests==2.25.1

python-install: ### Install and configure Python - optional: PYTHON_VERSION
	if [ $(SYSTEM_DIST) == macos ]; then
		brew unlink python@$(PYTHON_VERSION_MAJOR).$(PYTHON_VERSION_MINOR); brew link --overwrite --force python@$(PYTHON_VERSION_MAJOR).$(PYTHON_VERSION_MINOR)
		rm -f $$(brew --prefix)/bin/python
		ln $$(brew --prefix)/bin/python3 $$(brew --prefix)/bin/python
	fi
	[ -d $$HOME/.pyenv/.git ] && ( cd $$HOME/.pyenv; git pull ) || ( rm -rf $$HOME/.pyenv; git clone https://github.com/pyenv/pyenv.git $$HOME/.pyenv )
	pyenv install --skip-existing $(PYTHON_VERSION)
	python -m pip install --upgrade pip
	pip install $(PYTHON_BASE_PACKAGES)
	pyenv global $(PYTHON_VERSION)

python-virtualenv: ### Setup Python virtual environment - optional: PYTHON_VERSION,PYTHON_VENV_NAME
	pyenv install --skip-existing $(PYTHON_VERSION)
	if [ -z "$(PYTHON_VENV_NAME)" ]; then
		pyenv local $(PYTHON_VERSION)
		pip install --upgrade pip
		pip install $(PYTHON_BASE_PACKAGES)
		sed -i 's;    "python.linting.flake8Path":.*;    "python.linting.flake8Path": "~/.pyenv/versions/$(PYTHON_VERSION)/bin/flake8",;g' project.code-workspace 2> /dev/null ||:
		sed -i 's;    "python.linting.mypyPath":.*;    "python.linting.mypyPath": "~/.pyenv/versions/$(PYTHON_VERSION)/bin/mypy",;g' project.code-workspace 2> /dev/null ||:
		sed -i 's;    "python.linting.pylintPath":.*;    "python.linting.pylintPath": "~/.pyenv/versions/$(PYTHON_VERSION)/bin/pylint",;g' project.code-workspace 2> /dev/null ||:
		sed -i 's;    "python.pythonPath":.*;    "python.pythonPath": "~/.pyenv/versions/$(PYTHON_VERSION)/bin/python",;g' project.code-workspace 2> /dev/null ||:
	else
		pyenv virtualenv $(PYTHON_VERSION) $(PYTHON_VENV_NAME)
		pyenv local $(PYTHON_VENV_NAME)
		pip install --upgrade pip
		pip install $(PYTHON_BASE_PACKAGES)
		sed -i 's;    "python.linting.flake8Path":.*;    "python.linting.flake8Path": "~/.pyenv/versions/$(PYTHON_VENV_NAME)/bin/flake8",;g' project.code-workspace 2> /dev/null ||:
		sed -i 's;    "python.linting.mypyPath":.*;    "python.linting.mypyPath": "~/.pyenv/versions/$(PYTHON_VENV_NAME)/bin/mypy",;g' project.code-workspace 2> /dev/null ||:
		sed -i 's;    "python.linting.pylintPath":.*;    "python.linting.pylintPath": "~/.pyenv/versions/$(PYTHON_VENV_NAME)/bin/pylint",;g' project.code-workspace 2> /dev/null ||:
		sed -i 's;    "python.pythonPath":.*;    "python.pythonPath": "~/.pyenv/versions/$(PYTHON_VENV_NAME)/bin/python",;g' project.code-workspace 2> /dev/null ||:
	fi

python-virtualenv-clean: ### Clean up Python virtual environment - optional: PYTHON_VERSION=[version or venv name]
	pyenv uninstall --force $(PYTHON_VERSION)
	rm -rf .python-version

python-code-format: ### Format Python code with 'black' - optional: FILES=[directory, file or pattern]
	make docker-run-tools CMD=" \
		black \
			--line-length 120 \
			$(or $(FILES), $(APPLICATION_DIR)) \
	"

python-code-check: ### Check Python code with 'flake8' - optional: FILES=[directory, file or pattern],EXCLUDE=[comma-separated list]
	make docker-run-tools CMD=" \
		flake8 \
			--max-line-length=120 \
			--exclude */tests/__init__.py,$(EXCLUDE) \
			$(or $(FILES), $(APPLICATION_DIR)) \
	"

python-code-coverage: ### Test Python code with 'coverage' - mandatory: CMD=[test program]; optional: FILES=[directory, file or pattern],EXCLUDE=[comma-separated list]
	make docker-run-tools SH=y CMD=" \
		coverage run \
			--source=$(or $(FILES), $(APPLICATION_DIR)) \
			--omit=*/tests/*,$(EXCLUDE) \
			$(CMD) &&
		coverage report -m && \
		coverage erase \
	"

python-clean: ### Clean up Python project files - mandatory: DIR=[Python project directory]
	[ -z "$(DIR)" ] && (echo "ERROR: Please, specify the DIR"; exit 1)
	find $(DIR) \( \
		-name "__pycache__" -o \
		-name ".mypy_cache" -o \
		-name "*.pyc" -o \
		-name "*.pyd" -o \
		-name "*.pyo" -o \
		-name "coverage.xml" -o \
		-name "db.sqlite3" -o \
	\) -print | xargs rm -rfv

python-check-versions: ### Check Python versions alignment
	echo "python library: $(PYTHON_VERSION) (current $(DEVOPS_PROJECT_VERSION))"
	echo "python library aws: none"
	echo "python virtual: $$(pyenv install --list | grep -v - | grep -v b | tail -1 | sed "s/^[[:space:]]*//g") (latest)"
	echo "python docker: $$(make docker-repo-list-tags REPO=python | grep -w "^[0-9]*\(\.[0-9]*\(\.[0-9]*\)\?\)\?-alpine$$" | sort -V -r | head -n 1 | sed "s/-alpine//g" | sed "s/^[[:space:]]*//g") (latest)"
	echo "python aws: unknown"

.SILENT: \
	python-check-versions
