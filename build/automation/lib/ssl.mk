SSL_CERTIFICATE_DIR = $(ETC_DIR)/certificate
SSL_CERTIFICATE_VALID_DAYS = 397

# ==============================================================================

ssl-generate-certificate-project: ### Generate self-signed certificate for the project - optional: SSL_DOMAINS='*.domain1,*.domain2'
	domains="localhost,DNS:$(PROJECT_NAME_SHORT).local,DNS:*.$(PROJECT_NAME_SHORT).local,DNS:$(PROJECT_NAME).local,DNS:*.$(PROJECT_NAME).local,"
	domains+="DNS:$(PROJECT_NAME_SHORT)-$(PROJECT_GROUP_SHORT).local,DNS:*.$(PROJECT_NAME_SHORT)-$(PROJECT_GROUP_SHORT).local,"
	domains+="DNS:*.$(TEXAS_HOSTED_ZONE_NONPROD),DNS:*.$(TEXAS_HOSTED_ZONE_PROD),"
	for domain in $$(echo $(SSL_DOMAINS) | tr "," "\n"); do
		domains+="DNS:$${domain},"
	done
	make ssl-generate-certificate \
		DIR=$(SSL_CERTIFICATE_DIR) \
		NAME=certificate \
		SSL_DOMAINS=$$(printf "$$domains" | head -c -1)

ssl-print-certificate-info-project: ### Print inforamtion about the self-signed certificate for the project
	openssl x509 -in $(SSL_CERTIFICATE_DIR)/certificate.pem -text

ssl-copy-certificate-project: ### Copy self-signed certificate for the project - mandatory: DIR=[new path for the certificate]
	if [ ! -f $(DIR)/certificate.pem ] || [ $$(md5sum $(SSL_CERTIFICATE_DIR)/certificate.pem | awk '{ print $$1 }') != $$(md5sum $(DIR)/certificate.pem | awk '{ print $$1 }') ]; then
		cp -fv $(SSL_CERTIFICATE_DIR)/certificate.* $(DIR)
	fi

ssl-trust-certificate-project: ### Trust self-signed certificate for the project
	if [ ! -f $(SSL_CERTIFICATE_DIR)/certificate.pem ]; then
		make ssl-generate-certificate-project
	fi
	make ssl-trust-certificate \
		FILE=$(SSL_CERTIFICATE_DIR)/certificate.pem

# ==============================================================================

ssl-request-certificate-prod: ### Request production certificate for the service - mandatory: SSL_DOMAINS_PROD='*.domain1,*.domain2'
	# TODO:

# ==============================================================================

ssl-generate-certificate: ### Generate self-signed certificate - mandatory: DIR=[path to certificate],NAME=[certificate file name],SSL_DOMAINS='*.domain1,DNS:*.domain2'
	rm -f $(DIR)/$(NAME).{crt,key,pem,p12}
	openssl req \
		-new -x509 -nodes -sha256 \
		-newkey rsa:4096 \
		-days $(SSL_CERTIFICATE_VALID_DAYS) \
		-subj "/O=$(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)/OU=$(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)/CN=$(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)" \
		-reqexts SAN \
		-extensions SAN \
		-config \
			<(cat /etc/ssl/openssl.cnf \
			<(printf '[SAN]\nsubjectAltName=DNS:$(SSL_DOMAINS)')) \
		-keyout $(DIR)/$(NAME).key \
		-out $(DIR)/$(NAME).crt
	cat $(DIR)/$(NAME).crt $(DIR)/$(NAME).key > $(DIR)/$(NAME).pem
	openssl pkcs12 \
		-export -passout pass: \
		-in $(DIR)/$(NAME).crt \
		-inkey $(DIR)/$(NAME).key \
		-out $(DIR)/$(NAME).p12
	openssl x509 -text < $(DIR)/$(NAME).crt

ssl-trust-certificate: ### Trust self-signed certificate - mandatory: FILE=[path to .pem file]
	sudo security add-trusted-cert -d \
		-r trustRoot \
		-k /Library/Keychains/System.keychain \
		$(FILE)
	file=/etc/hosts
	sudo make file-remove-content \
		FILE=$$file \
		CONTENT="\n# BEGIN: $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)(.)*# END: $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)\n"
	echo -e "\n# BEGIN: $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)" | sudo tee -a $$file
	echo "127.0.0.1 $(PROJECT_NAME_SHORT).local" | sudo tee -a $$file
	echo "127.0.0.1 $(PROJECT_NAME).local" | sudo tee -a $$file
	echo "127.0.0.1 $(PROJECT_NAME_SHORT)-$(PROJECT_GROUP_SHORT).local" | sudo tee -a $$file
	echo "# END: $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)" | sudo tee -a $$file
	dscacheutil -flushcache
