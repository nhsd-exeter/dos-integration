test-k8s:
	make test-k8s-setup
	tests=( \
		test-k8s-create-base-from-template \
		test-k8s-create-overlay-from-template \
		test-k8s-deploy \
		test-k8s-undeploy \
		test-k8s-deploy-job \
		test-k8s-undeploy-job \
		test-k8s-alb-get-ingress-endpoint \
		test-k8s-replace-variables \
		test-k8s-get-namespace-ttl \
		test-k8s-kubeconfig-get \
		test-k8s-kubeconfig-export-variables \
		test-k8s-clean \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-k8s-teardown

test-k8s-setup:
	:

test-k8s-teardown:
	rm -rf $(DEPLOYMENT_DIR)

# ==============================================================================

test-k8s-create-base-from-template:
	mk_test_skip

test-k8s-create-overlay-from-template:
	mk_test_skip

test-k8s-deploy:
	mk_test_skip

test-k8s-undeploy:
	mk_test_skip

test-k8s-deploy-job:
	mk_test_skip

test-k8s-undeploy-job:
	mk_test_skip

test-k8s-alb-get-ingress-endpoint:
	mk_test_skip

test-k8s-replace-variables:
	# arrange
	make k8s-create-base-from-template STACK=application
	make k8s-create-overlay-from-template STACK=application PROFILE=live
	# act
	make k8s-replace-variables STACK=application PROFILE=live
	# assert
	cbase=$$(find $(K8S_DIR)/application/base -type f -name '*.yaml' -print | grep -v '/template/' | wc -l)
	cover=$$(find $(K8S_DIR)/application/overlays/live -type f -name '*.yaml' -print | grep -v '/template/' | wc -l)
	mk_test "base" "8 -eq $$cbase"
	mk_test "overlays" "2 -eq $$cover"
	mk_test_complete
	# clean up
	rm -rf $(K8S_DIR)/application

test-k8s-get-namespace-ttl:
	# act
	ttl=$$(make k8s-get-namespace-ttl)
	# assert
	mk_test "0 -eq $$(date -d $$ttl > /dev/null 2>&1; echo $$?)"

test-k8s-kubeconfig-get:
	mk_test_skip

test-k8s-kubeconfig-export-variables:
	# act
	export=$$(make k8s-kubeconfig-export-variables)
	# assert
	mk_test "1 -eq $$(echo $$export | grep 'export KUBECONFIG=' | wc -l)"

test-k8s-clean:
	# act
	make k8s-clean
	# assert
	count=$$(find $(K8S_DIR) -type f -name '*.yaml' -print | grep '/effective/' | wc -l)
	mk_test "0 -eq $$count"
