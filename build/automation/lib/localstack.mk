LOCALSTACK_HOST = localstack.$(PROJECT_NAME_SHORT).local
LOCALSTACK_VERSION = 0.12.11

localstack-start: project-config _localstack-copy-ssl-certificate ### Start localstack
	mkdir -p $(TMP_DIR)/localstack
	cp -f $(LIB_DIR)/localstack/server.test.* $(TMP_DIR)/localstack
	make docker-compose-start YML=$(LIB_DIR)/localstack/docker-compose.localstack.yml
	sleep 5

localstack-stop: ### Stop localstack
	make docker-compose-stop YML=$(LIB_DIR)/localstack/docker-compose.localstack.yml
	rm -rf $(TMP_DIR)/localstack

# ==============================================================================

_localstack-copy-ssl-certificate:
	make ssl-copy-certificate-project DIR=$(LIB_DIR)/localstack
	mv -f $(LIB_DIR)/localstack/certificate.crt $(LIB_DIR)/localstack/server.test.crt
	mv -f $(LIB_DIR)/localstack/certificate.key $(LIB_DIR)/localstack/server.test.key
	mv -f $(LIB_DIR)/localstack/certificate.p12 $(LIB_DIR)/localstack/server.test.p12
	mv -f $(LIB_DIR)/localstack/certificate.pem $(LIB_DIR)/localstack/server.test.pem
