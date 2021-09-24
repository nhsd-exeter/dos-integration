TEST_FILE = $(TMP_DIR_REL)/test-file.txt

test-file:
	make test-file-setup
	tests=( \
		test-file-remove-multiline-content \
		test-file-replace-multiline-content \
		test-file-replace-variables \
		test-file-replace-variables-dollar \
		test-file-replace-variables-dollar-curly-braces \
		test-file-replace-variables-file-name \
		test-file-replace-variables-file-name-exclude-file-name \
		test-file-replace-variables-in-dir \
		test-file-copy-and-replace \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-file-teardown

test-file-setup:
	:

test-file-teardown:
	:

# ==============================================================================

test-file-remove-multiline-content:
	# arrange
	echo -e "this\nis\na\nmultiline\nfile" > $(TEST_FILE)
	# act
	make file-remove-content \
		FILE=$(TEST_FILE) \
		CONTENT="this(.)*multiline\n"
	# assert
	mk_test "file = $$(cat $(TEST_FILE))"
	# clean up
	rm -f $(TEST_FILE)

test-file-replace-multiline-content:
	# arrange
	echo -e "this\nis\na\nmultiline\nfile" > $(TEST_FILE)
	# act
	make file-replace-content \
		FILE=$(TEST_FILE) \
		OLD="this(.)*file\n" \
		NEW="string"
	# assert
	mk_test "string = $$(cat $(TEST_FILE))"
	# clean up
	rm -f $(TEST_FILE)

test-file-replace-variables:
	# arrange
	echo VARIABLE_TO_REPLACE > $(TEST_FILE)
	# act
	export VARIABLE=this_is_a_test
	make file-replace-variables FILE=$(TEST_FILE)
	# assert
	mk_test "this_is_a_test = $$(cat $(TEST_FILE))"
	# clean up
	rm -f $(TEST_FILE)

test-file-replace-variables-dollar:
	# arrange
	echo 'Aaa_$$VARIABLE_TO_REPLACE_aaA' > $(TEST_FILE)
	# act
	export VARIABLE=this_is_a_test
	make file-replace-variables FILE=$(TEST_FILE)
	# assert
	mk_test "Aaa_this_is_a_test_aaA = $$(cat $(TEST_FILE))"
	# clean up
	rm -f $(TEST_FILE)

test-file-replace-variables-dollar-curly-braces:
	# arrange
	echo 'Aaa_$${VARIABLE_TO_REPLACE}_aaA' > $(TEST_FILE)
	# act
	export VARIABLE=this_is_a_test
	make file-replace-variables FILE=$(TEST_FILE)
	# assert
	mk_test "Aaa_this_is_a_test_aaA = $$(cat $(TEST_FILE))"
	# clean up
	rm -f $(TEST_FILE)

test-file-replace-variables-file-name:
	# arrange
	echo VARIABLE_TO_REPLACE > $(TEST_FILE).VARIABLE_TO_REPLACE
	# act
	export VARIABLE=this_is_a_test
	make file-replace-variables FILE=$(TEST_FILE).VARIABLE_TO_REPLACE
	# assert
	mk_test "this_is_a_test = $$(cat $(TEST_FILE).$$VARIABLE)"
	# clean up
	rm -f $(TEST_FILE).*

test-file-replace-variables-file-name-exclude-file-name:
	# arrange
	echo VARIABLE_TO_REPLACE > $(TEST_FILE).VARIABLE_TO_REPLACE
	# act
	export VARIABLE=this_is_a_test
	make file-replace-variables FILE=$(TEST_FILE).VARIABLE_TO_REPLACE EXCLUDE_FILE_NAME=true
	# assert
	mk_test "this_is_a_test = $$(cat $(TEST_FILE).VARIABLE_TO_REPLACE)"
	# clean up
	rm -f $(TEST_FILE).*

test-file-replace-variables-in-dir:
	mk_test_skip

test-file-copy-and-replace:
	# arrange
	echo "this_is_a_test" > $(TEST_FILE)
	# act
	make file-copy-and-replace \
		SRC=$(TEST_FILE) \
		DEST=$(TMP_DIR_REL)/$(@)_$(BUILD_ID) && \
		trap "rm -f $(TMP_DIR_REL)/$(@)_$(BUILD_ID)" EXIT
	# assert
	mk_test "this_is_a_test = $$(cat $(TEST_FILE))"
	# clean up
	rm -f $(TEST_FILE)
