test-java:
	make test-java-setup
	tests=( \
		test-java-virtualenv \
		test-java-virtualenv-clean \
		test-java-clean \
		test-java-add-certificate-to-keystore \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-java-teardown

test-java-setup:
	:

test-java-teardown:
	:

test-java-virtualenv:
	mk_test_skip

test-java-virtualenv-clean:
	mk_test_skip

test-java-clean:
	mk_test_skip

test-java-add-certificate-to-keystore:
	mk_test_skip
