test-python:
	make test-python-setup
	tests=( \
		test-python-virtualenv \
		test-python-virtualenv-clean \
		test-python-code-format \
		test-python-code-check \
		test-python-code-coverage \
		test-python-clean \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-python-teardown

test-python-setup:
	:

test-python-teardown:
	:

# ==============================================================================

test-python-virtualenv:
	mk_test_skip_if_not_macos $(@) && exit ||:
	# act
	make python-virtualenv
	# assert
	mk_test "$(PYTHON_VERSION) = $$(python --version | awk '{ print $$2 }')"

test-python-virtualenv-clean:
	mk_test_skip_if_not_macos $(@) && exit ||:
	# act
	make python-virtualenv-clean
	# assert
	mk_test "system = $$(pyenv version | grep -o ^system)"

test-python-code-format:
	# act & assert
	make -s python-code-format FILES=build/automation/bin/*.py && \
		mk_test "true" || mk_test "false"

test-python-code-check:
	# act & assert
	make -s python-code-check FILES=build/automation/bin/*.py && \
		mk_test "true" || mk_test "false"

test-python-code-coverage:
	mk_test_skip

test-python-clean:
	mk_test_skip
