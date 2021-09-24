secret-get-random-string secret-random: ### Generate random string - optional: LENGTH=[integer]
	str=
	if [ "$$OS" == "unix" ]; then
		str=$$(env LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c $(or $(LENGTH), 32))
	else
		str=</dev/urandom LC_ALL=C tr -dc A-Za-z0-9 | (head -c $$ > /dev/null 2>&1 || head -c $(or $(LENGTH), 32))
	fi
	echo "$$str"

secret-fetch-and-export-variables: ### Get secret and print variable exports - mandatory: NAME=[secret name]; return: [variables export]
	# set up
	eval "$$(make aws-assume-role-export-variables)"
	# fetch
	secret=$$(make aws-secret-get NAME=$(NAME))
	make _secret-export-variables-from-json JSON="$$secret"

secret-fetch: ### Get secret - mandatory: NAME=[secret name]; return: [json object]
	# set up
	eval "$$(make aws-assume-role-export-variables)"
	# fetch
	make aws-secret-get NAME=$(NAME)

secret-create: ### Set secret - mandatory: NAME=[secret name], VARS=[comma-separated environment variable names]
	# set up
	eval "$$(make aws-assume-role-export-variables)"
	# create
	json=
	for key in $$(echo "$(VARS)" | sed 's/,/\n/g'); do
		value=$$(echo $$(eval echo "\$$$$key"))
		json+="\"$${key}\":\"$${value}\","
	done
	file=$(TMP_DIR)/$(@)_$(BUILD_ID)
	echo "{$${json%?}}" > $$file && trap "rm -f $$file" EXIT
	make aws-secret-create NAME=$(NAME) VALUE=file://$$file

secret-get-existing-value: ### Get secret key value - mandatory: NAME=[secret name]; optional: KEY=[secret key]; return [key value]
	eval "$$(make aws-assume-role-export-variables)"
	secret=$$(make secret-fetch NAME=$(NAME))
	if [ -n "$(KEY)" ] && [[ $$secret == {*} ]]; then
		echo $$secret | make -s docker-run-tools CMD="jq -r '.$(KEY)'"
	else
		echo $$secret
	fi

secret-update-existing-value: ### Update existing secret key with given key/value pair - mandatory: NAME=[secret name],KEY=[secret key],VALUE=[new key value]
	eval "$$(make aws-assume-role-export-variables)"
	secrets=$$(make secret-fetch NAME=$(NAME))
	file=$(TMP_DIR)/$(@)_$(BUILD_ID)
	echo $$secrets | make -s docker-run-tools CMD="jq '.$(KEY) = \"$(VALUE)\"'" > $$file # && trap "rm -f $$file" EXIT
	make aws-secret-put NAME=$(NAME) VALUE=file://$$file

secret-copy-value-from: ### Copy secret key value - mandatory: SRC_NAME=[secret name],DEST_NAME=[secret name],KEY=[secret key]
	eval "$$(make aws-assume-role-export-variables)"
	value=$$(make secret-get-existing-value NAME=$(SRC_NAME) KEY=$(KEY))
	make secret-update-existing-value NAME=$(DEST_NAME) KEY=$(KEY) VALUE=$$value

# ==============================================================================

_secret-export-variables-from-json: ### Convert JSON to environment variables - mandatory: JSON='{"key":"value"}'|JSON="$$(echo '$(JSON)')"; return: [variables export]
	OLDIFS=$$IFS; IFS=$$'\n';
	for str in $$(echo '$(JSON)' | make -s docker-run-tools CMD="jq -rf $(JQ_DIR_REL)/json-to-env-vars.jq" | sort); do
		key=$$(cut -d "=" -f1 <<<"$$str")
		value=$$(cut -d "=" -f2- <<<"$$str")
		echo "export $${key}='$$(echo $${value} | sed -e 's/[[:space:]]/_/g')'"
	done
	IFS=$$OLDIFS
	make terraform-export-variables-from-json JSON="$$(echo '$(JSON)')"

# ==============================================================================

.SILENT: \
	_secret-export-variables-from-json \
	secret-create \
	secret-fetch \
	secret-fetch-and-export-variables \
	secret-get-existing-value \
	secret-get-random-string \
	secret-random
