test-slack:
	make test-slack-setup
	tests=( \
		test-slack-send-notification \
		test-slack-send-template-notification \
		test-slack-render-template \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-slack-teardown

test-slack-setup:
	:

test-slack-teardown:
	:

test-slack-send-notification:
	mk_test_skip

test-slack-send-template-notification:
	mk_test_skip

test-slack-render-template:
	mk_test_skip
