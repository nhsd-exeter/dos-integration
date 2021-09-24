TEST_CERT = custom-domain.com

test-ssl:
	make test-ssl-setup
	tests=( \
		test-ssl-generate-certificate-single-domain \
		test-ssl-generate-certificate-multiple-domains \
		test-ssl-generate-certificate-project \
		test-ssl-print-certificate-info-project \
		test-ssl-copy-certificate-project \
		test-ssl-trust-certificate-project \
		test-ssl-trust-certificate \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-ssl-teardown

test-ssl-setup:
	:

test-ssl-teardown:
	rm -rf $(TMP_DIR)/*.{crt,key,p12,pem}
	if [ $(PROJECT_NAME) == $(DEVOPS_PROJECT_NAME) ]; then
		mk_test_proceed_if_macos && (
			sudo security find-certificate -c $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT) -a -Z | \
			sudo awk '/SHA-1/{system("security delete-certificate -Z "$$NF)}' && \
			sudo make file-remove-content \
				FILE=/etc/hosts \
				CONTENT="\n# BEGIN: $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)(.)*# END: $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)\n" \
		)
		rm -rf $(SSL_CERTIFICATE_DIR)/certificate.{crt,key,p12,pem}
		rm -rf $(TMP_DIR)/*.{crt,key,p12,pem}
	fi

# ==============================================================================

test-ssl-generate-certificate-single-domain:
	# act
	make ssl-generate-certificate \
		DIR=$(TMP_DIR) \
		NAME=$(TEST_CERT) \
		SSL_DOMAINS=single-$(TEST_CERT)
	# assert
	mk_test "-f $(TMP_DIR)/$(TEST_CERT).pem"

test-ssl-generate-certificate-multiple-domains:
	# act
	make ssl-generate-certificate \
		DIR=$(TMP_DIR) \
		NAME=multi-$(TEST_CERT) \
		SSL_DOMAINS=multi-$(TEST_CERT),DNS:*.multi-$(TEST_CERT),DNS:platform.com,DNS:*.platform.com
	# assert
	mk_test "-f $(TMP_DIR)/multi-$(TEST_CERT).pem"

test-ssl-generate-certificate-project:
	# act
	make ssl-generate-certificate-project SSL_DOMAINS=platform.com,*.platform.com
	# assert
	mk_test "-f $(SSL_CERTIFICATE_DIR)/certificate.pem"

test-ssl-print-certificate-info-project:
	# arrange
	make ssl-generate-certificate-project SSL_DOMAINS=platform.com,*.platform.com
	# act
	output=$$(make ssl-print-certificate-info-project | grep -Eo "DNS:platform.com" | wc -l)
	# assert
	mk_test "1 -eq $$output"

test-ssl-copy-certificate-project:
	# arrange
	rm -f $(TMP_DIR)/certificate.*
	# act
	make ssl-copy-certificate-project DIR=$(TMP_DIR)
	# assert
	mk_test "-f $(TMP_DIR)/certificate.pem"

test-ssl-trust-certificate-project:
	mk_test_skip_if_not_macos $(@) && exit ||:
	# arrange
	make ssl-generate-certificate-project
	# act
	make ssl-trust-certificate \
		FILE=$(TMP_DIR)/$(TEST_CERT).pem
	# assert
	mk_test "keychain" "0 -lt $$(sudo security find-certificate -a -c $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT) | grep -Eo 'alis(.*)$(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)' | wc -l)"
	mk_test "hosts file" "3 -eq $$(cat /etc/hosts | grep -E '$(PROJECT_NAME_SHORT).local|$(PROJECT_NAME).local|$(PROJECT_NAME_SHORT)-$(PROJECT_GROUP_SHORT).local' | wc -l)"
	mk_test_complete

test-ssl-trust-certificate:
	mk_test_skip_if_not_macos $(@) && exit ||:
	# arrange
	make ssl-generate-certificate \
		DIR=$(TMP_DIR) \
		NAME=$(TEST_CERT) \
		SSL_DOMAINS=$(TEST_CERT),DNS:*.$(TEST_CERT),DNS:other-domain.com,DNS:*.other-domain.com
	# act
	make ssl-trust-certificate \
		FILE=$(TMP_DIR)/$(TEST_CERT).pem
	# assert
	mk_test "keychain" "0 -lt $$(sudo security find-certificate -a -c $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT) | grep -Eo 'alis(.*)$(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)' | wc -l)"
	mk_test "hosts file" "3 -eq $$(cat /etc/hosts | grep -E '$(PROJECT_NAME_SHORT).local|$(PROJECT_NAME).local|$(PROJECT_NAME_SHORT)-$(PROJECT_GROUP_SHORT).local' | wc -l)"
	mk_test_complete
