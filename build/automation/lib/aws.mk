aws-session-fail-if-invalid: ### Fail if the session variables are not set
	([ -z "$$AWS_ACCESS_KEY_ID" ] || [ -z "$$AWS_SECRET_ACCESS_KEY" ] || [ -z "$$AWS_SESSION_TOKEN" ]) \
		&& exit 1 ||:

aws-assume-role-export-variables: ### Get assume role export for the pipeline user - optional: AWS_ACCOUNT_ID|PROFILE=[profile name to load relevant platform configuration file]
	if [ "$(AWS_ROLE)" == $(AWS_ROLE_PIPELINE) ]; then
		if [ $(AWS_ACCOUNT_ID) == "$$(make aws-account-get-id)" ] && [ $(AWS_ACCOUNT_ID) != $(AWS_ACCOUNT_ID_MGMT) ]; then
			echo "Already assumed arn:aws:iam::$(AWS_ACCOUNT_ID):role/$(AWS_ROLE)" >&2
			exit
		fi
		array=($$(
			make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
				$(AWSCLI) sts assume-role \
					--role-arn arn:aws:iam::$(AWS_ACCOUNT_ID):role/$(AWS_ROLE) \
					--role-session-name $(AWS_ROLE_SESSION) \
					--query=Credentials.[AccessKeyId,SecretAccessKey,SessionToken] \
					--output text \
				| sed -E 's/[[:blank:]]+/ /g' \
			"
		))
		echo "export AWS_ACCESS_KEY_ID=$${array[0]}"
		echo "export AWS_SECRET_ACCESS_KEY=$${array[1]}"
		echo "export AWS_SESSION_TOKEN=$${array[2]}"
	fi

aws-user-get-role:
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) sts get-caller-identity \
		--query 'Arn' \
		--output text \
	" | grep -Eo 'assumed-role/.*/' | sed 's;assumed-role/;;g' | sed 's;/;;g' | tr -d '\r' | tr -d '\n'

aws-account-check-id: ### Check if user has MFA'd into the account - mandatory: ID=[AWS account number]; return: true|false
	if [ $(ID) == "$$(make aws-account-get-id)" ] && [ "$$TEXAS_SESSION_EXPIRY_TIME" -gt $$(date -u +"%Y%m%d%H%M%S") ]; then
		echo true
	else
		echo false
	fi

aws-account-get-id: ### Get the account ID user has MFA'd into - return: AWS account number
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) sts get-caller-identity \
		--query 'Account' \
		--output text \
	" | tr -d '\r' | tr -d '\n'

aws-secret-create: ### Create a new secret and save the value - mandatory: NAME=[secret name]; optional: VALUE=[string or file://file.json],AWS_REGION=[AWS region]
	if [ "false" == $$(make aws-secret-exists NAME=$(NAME)) ]; then
		make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
			$(AWSCLI) secretsmanager create-secret \
				--name $(NAME) \
				--region $(AWS_REGION) \
				--tags Key=Programme,Value=$(PROGRAMME) Key=Service,Value=$(SERVICE_TAG) Key=Environment,Value=$(ENVIRONMENT) Key=Profile,Value=$(PROFILE) \
				--output text \
		"
	else
		echo "Secret '$(NAME)' already exists!"
	fi
	if [ -n "$(VALUE)" ]; then
		make aws-secret-put NAME=$(NAME) VALUE=$(VALUE) AWS_REGION=$(AWS_REGION)
	fi

aws-secret-put: ### Put secret value in the specified secret - mandatory: NAME=[secret name],VALUE=[string or file://file.json]; optional: AWS_REGION=[AWS region]
	file=$$(echo $(VALUE) | grep -E "^file://" > /dev/null 2>&1 && echo $(VALUE) | sed 's;file://;;g' ||:)
	[ -n "$$file" ] && volume="--volume $$file:$$file" || volume=
	make -s docker-run-tools ARGS="$$volume $$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) secretsmanager put-secret-value \
			--secret-id $(NAME) \
			--secret-string "$(VALUE)" \
			--version-stage AWSCURRENT \
			--region $(AWS_REGION) \
			--output text \
	"

aws-secret-get: ### Get secret - mandatory: NAME=[secret name]; optional: AWS_REGION=[AWS region]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) secretsmanager get-secret-value \
			--secret-id $(NAME) \
			--version-stage AWSCURRENT \
			--region $(AWS_REGION) \
			--query '{SecretString: SecretString}' \
			--output text \
	" | tr -d '\r' | tr -d '\n'

aws-secret-get-and-format: ### Get secret - mandatory: NAME=[secret name]; optional: AWS_REGION=[AWS region]
	make aws-secret-get NAME=$(NAME) \
		| make -s docker-run-tools CMD="jq -r"

aws-secret-exists: ### Check if secret exists - mandatory: NAME=[secret name]; optional: AWS_REGION=[AWS region]; return: true|false
	count=$$(make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) secretsmanager list-secrets \
			--region $(AWS_REGION) \
			--query 'SecretList[*].Name' \
			--output text \
	" | grep $(NAME) | wc -l)
	[ 0 -eq $$count ] && echo false || echo true

aws-iam-policy-create: ### Create IAM policy - mandatory: NAME=[policy name],DESCRIPTION=[policy description],FILE=[path to json file]
	file=$(TMP_DIR_REL)/$(@)_$(BUILD_ID)
	make file-copy-and-replace SRC=$(FILE) DEST=$$file && trap "rm -f $$file" EXIT
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) iam create-policy \
			--policy-name $(NAME) \
			--policy-document file://$$file \
			--description '$(DESCRIPTION)' \
	"

aws-iam-policy-exists: ### Check if IAM policy exists - mandatory: NAME=[policy name]; return: true|false
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) iam get-policy \
			--policy-arn arn:aws:iam::$(AWS_ACCOUNT_ID):policy/$(NAME) \
	" > /dev/null 2>&1 && echo true || echo false

aws-iam-role-create: ### Create IAM role - mandatory: NAME=[role name],DESCRIPTION=[role description],FILE=[path to json file]
	file=$(TMP_DIR_REL)/$(@)_$(BUILD_ID)
	make file-copy-and-replace SRC=$(FILE) DEST=$$file && trap "rm -f $$file" EXIT
	tags='[{"Key":"Programme","Value":"$(PROGRAMME)"},{"Key":"Service","Value":"$(SERVICE_TAG)"},{"Key":"Environment","Value":"$(ENVIRONMENT)"},{"Key":"Profile","Value":"$(PROFILE)"}]'
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) iam create-role \
			--role-name $(NAME) \
			--assume-role-policy-document file://$$file \
			--description '$(DESCRIPTION)' \
			--tags '$$tags' \
	"

aws-iam-role-exists: ### Check if IAM role exists - mandatory: NAME=[role name]; return: true|false
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) iam get-role \
			--role-name $(NAME) \
	" > /dev/null 2>&1 && echo true || echo false

aws-iam-role-attach-policy: ### Attach IAM policy to role IAM role - mandatory: ROLE_NAME=[role name],POLICY_NAME=[policy name]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) iam attach-role-policy \
			--role-name $(ROLE_NAME) \
			--policy-arn arn:aws:iam::$(AWS_ACCOUNT_ID):policy/$(POLICY_NAME) \
	"

aws-s3-create: ### Create secure bucket - mandatory: NAME=[bucket name]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) s3api create-bucket \
			--bucket $(NAME) \
			--acl private \
			--create-bucket-configuration LocationConstraint=$(AWS_REGION) \
			--region $(AWS_REGION) \
	"
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) s3api put-public-access-block \
			--bucket $(NAME) \
			--public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" \
	"
	json='{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) s3api put-bucket-encryption \
			--bucket $(NAME) \
			--server-side-encryption-configuration '$$json' \
	"
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) s3api put-bucket-versioning \
			--bucket $(NAME) \
			--versioning-configuration "Status=Enabled" \
	"
	tags='TagSet=[{Key=Programme,Value=$(PROGRAMME)},{Key=Service,Value=$(SERVICE_TAG)},{Key=Environment,Value=$(ENVIRONMENT)},{Key=Profile,Value=$(PROFILE)}]'
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) s3api put-bucket-tagging \
			--bucket $(NAME) \
			--tagging '$$tags' \
	"

aws-s3-upload: ### Upload file to bucket - mandatory: FILE=[local path (inside container)],URI=[remote path]; optional: ARGS=[S3 cp options]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) s3 cp \
			$(FILE) \
			s3://$(URI) \
			$(ARGS) \
	"

aws-s3-download: ### Download file from bucket - mandatory: URI=[remote path],FILE=[local path (inside container)]; optional: ARGS=[S3 cp options]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) s3 cp \
			s3://$(URI) \
			$(FILE) \
			$(ARGS) \
	"

aws-s3-exists: ### Check if bucket exists - mandatory: NAME=[bucket name]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) s3 ls \
			s3://$(NAME) \
		2>&1 | grep -q NoSuchBucket \
	" > /dev/null 2>&1 && echo false || echo true

aws-dynamodb-create: ### Create DynamoDB table - mandatory: NAME=[table name],ATTRIBUTE_DEFINITIONS,KEY_SCHEMA; optional: PROVISIONED_THROUGHPUT
	default_throughput="ReadCapacityUnits=1,WriteCapacityUnits=1"
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) dynamodb create-table \
			--table-name $(NAME) \
			--attribute-definitions $(ATTRIBUTE_DEFINITIONS) \
			--key-schema $(KEY_SCHEMA) \
			--provisioned-throughput $(or $(PROVISIONED_THROUGHPUT), $$default_throughput) \
			--tags Key=Programme,Value=$(PROGRAMME) Key=Service,Value=$(SERVICE_TAG) Key=Environment,Value=$(ENVIRONMENT) Key=Profile,Value=$(PROFILE) \
	"

aws-dynamodb-put-item: ### Create DynamoDB item - mandatory: NAME=[table name],ITEM=[json or file://file.json]
	file=$$(echo '$(ITEM)' | grep -E "^file://" > /dev/null 2>&1 && echo $(ITEM) | sed 's;file://;;g' ||:)
	[ -n "$$file" ] && volume="--volume $$file:$$file" || volume=
	json='$(ITEM)'
	make -s docker-run-tools ARGS="$$volume $$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) dynamodb put-item \
			--table-name $(NAME) \
			--item '$$json' \
			--return-consumed-capacity TOTAL \
			--return-item-collection-metrics SIZE \
	"

aws-dynamodb-query: ### Query DynamoDB table - mandatory: NAME=[table name],CONDITION_EXPRESSION,EXPRESSION_ATTRIBUTES=[json or file://file.json]
	file=$$(echo '$(EXPRESSION_ATTRIBUTES)' | grep -E "^file://" > /dev/null 2>&1 && echo $(EXPRESSION_ATTRIBUTES) | sed 's;file://;;g' ||:)
	[ -n "$$file" ] && volume="--volume $$file:$$file" || volume=
	json='$(EXPRESSION_ATTRIBUTES)'
	make -s docker-run-tools ARGS="$$volume $$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) dynamodb query \
			--table-name $(NAME) \
			--key-condition-expression "$(CONDITION_EXPRESSION)" \
			--expression-attribute-values '$$json' \
	"

aws-dynamodb-exists: ### Check if DynamoDB table exists - mandatory: NAME=[table name]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) dynamodb describe-table \
			--table-name $(NAME) \
			2>&1 | grep -q '\"TableName\": \"$(NAME)\"' \
	" > /dev/null 2>&1 && echo true || echo false

aws-rds-describe-instance: ### Describe RDS instance - mandatory: DB_INSTANCE
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) rds describe-db-instances \
			--region $(AWS_REGION) \
			--db-instance-identifier=$(DB_INSTANCE) \
	" | make -s docker-run-tools CMD="jq -r '.DBInstances[0]'"

aws-rds-create-snapshot: ### Create RDS instance snapshot - mandatory: DB_INSTANCE,SNAPSHOT_NAME
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		aws rds create-db-snapshot \
			--region $(AWS_REGION) \
			--db-instance-identifier $(DB_INSTANCE) \
			--db-snapshot-identifier $(SNAPSHOT_NAME) \
	"

aws-rds-get-snapshot-status: ### Get RDS snapshot status - mandatory: SNAPSHOT_NAME
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) rds describe-db-snapshots \
			--region $(AWS_REGION) \
			--db-snapshot-identifier $(SNAPSHOT_NAME) \
			--query 'DBSnapshots[].Status' \
			--output text \
	" | tr -d '\r' | tr -d '\n'

aws-rds-wait-for-snapshot: ### Wait for RDS snapshot to become available - mandatory: SNAPSHOT_NAME
	echo "Waiting for the snapshot to become available"
	count=0
	until [ $$count -ge 1800 ]; do
		if [ "$$(make aws-rds-get-snapshot-status SNAPSHOT_NAME=$(SNAPSHOT_NAME))" == "available" ]; then
			echo "The snapshot is available"
			exit 0
		fi
		sleep 1s
		((count++)) ||:
	done
	echo "ERROR: The snapshot has not become available"
	exit 1

aws-cognito-get-userpool-id: ### Get Cognito userpool ID - mandatory: NAME=[user pool name]; optional: AWS_REGION=[AWS region]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) cognito-idp list-user-pools \
			--region $(AWS_REGION) \
			--max-results 60 \
			--output text \
	" | grep $(NAME) | awk '{ print $$3 }'

aws-cognito-get-client-id: ### Get Cognito client ID - mandatory: NAME=[user pool name]; optional: AWS_REGION=[AWS region]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) cognito-idp list-user-pool-clients \
			--user-pool-id $$(make -s aws-cognito-get-userpool-id NAME=$(NAME)) \
			--region $(AWS_REGION) \
			--query 'UserPoolClients[].ClientId' \
			--output text \
	"

aws-cognito-get-client-secret: ### Get Cognito client secret - mandatory: NAME=[user pool name]; optional: AWS_REGION=[AWS region]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) cognito-idp describe-user-pool-client \
			--user-pool-id $$(make -s aws-cognito-get-userpool-id NAME=$(NAME)) \
			--client-id $$(make -s aws-cognito-get-client-id NAME=$(NAME)) \
			--region $(AWS_REGION) \
			--query 'UserPoolClient.ClientSecret' \
			--output text \
	"

aws-ecr-get-login-password: ### Get ECR user login password
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) ecr get-login-password --region $(AWS_REGION) \
	"

aws-ecr-create-repository: ### Create ECR repository to store an image - mandatory: NAME; optional: POLICY_FILE=[policy file]
	policy_file=$(or $(POLICY_FILE), $(LIB_DIR_REL)/aws/aws-ecr-create-repository-policy.json)
	effective_policy_file=$(TMP_DIR_REL)/$(@)_$(BUILD_ID)
	make file-copy-and-replace SRC=$$policy_file DEST=$$effective_policy_file && trap "rm -f $$effective_policy_file" EXIT
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) ecr create-repository \
			--repository-name $(PROJECT_GROUP_SHORT)/$(PROJECT_NAME_SHORT)/$(NAME) \
			--tags Key=Programme,Value=$(PROGRAMME) Key=Service,Value=$(SERVICE_TAG) \
	"
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) ecr set-repository-policy \
			--repository-name $(PROJECT_GROUP_SHORT)/$(PROJECT_NAME_SHORT)/$(NAME) \
			--policy-text file://$$effective_policy_file \
	"

aws-ecr-get-image-digest: ### Get ECR image digest by matching tag pattern - mandatory: REPO=[repository name],TAG=[string to match tag of an image]
	file=$(TMP_DIR_REL)/$(@)_$(BUILD_ID)
	make file-copy-and-replace SRC=$(JQ_DIR_REL)/aws-ecr-get-image-digest.jq DEST=$$file >&2 && trap "rm -f $$file" EXIT
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) ecr list-images \
			--repository-name $(shell echo $(REPO) | sed "s;$(AWS_ECR)/;;g") \
	" | make -s docker-run-tools CMD="jq -rf $$file" | head -n 1

aws-ses-verify-email-identity: ### Verify SES email address - mandatory: NAME
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) ses verify-email-identity \
			--email-address $(NAME) \
			--region $(AWS_ALTERNATIVE_REGION) \
	"

aws-codeartifact-crate-domain: ### Create CodeArtifact domain - optional: DOMAIN_NAME=[domain name]
	domain_name=$(or $(DOMAIN_NAME), $(ORG_NAME))
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) codeartifact create-domain \
			--domain $$domain_name \
			--tags key=Service,value=$(SERVICE_TAG_COMMON) \
			--region $(AWS_ALTERNATIVE_REGION) \
	"

aws-codeartifact-create-repository: ### Create CodeArtifact repository - mandatory: REPOSITORY_NAME=[repository name],UPSTREAMS=[]; optional: DOMAIN_NAME=[domain name]
	domain_name=$(or $(DOMAIN_NAME), $(ORG_NAME))
	upstreams=$$([ -n "$(UPSTREAMS)" ] && echo --upstreams $(UPSTREAMS) ||:)
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) codeartifact create-repository \
			--domain $$domain_name \
			--repository $(REPOSITORY_NAME) \
			$$upstreams \
			--tags key=Programme,value=$(PROGRAMME) key=Service,value=$(SERVICE_TAG) \
			--region $(AWS_ALTERNATIVE_REGION) \
	"

aws-codeartifact-associate-external-repository: ### Create CodeArtifact external repository association - mandatory: REPOSITORY_NAME=[repository name],EXTERNAL_NAME=[external repository name]; optional: DOMAIN_NAME=[domain name]
	domain_name=$(or $(DOMAIN_NAME), $(ORG_NAME))
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) codeartifact associate-external-connection \
			--domain $$domain_name \
			--repository $(REPOSITORY_NAME) \
			--external-connection public:$(EXTERNAL_NAME) \
			--region $(AWS_ALTERNATIVE_REGION) \
	"

aws-codeartifact-setup: ### Set up CodeArtifact - mandatory: REPOSITORY_NAME=[repository name]; optional: DOMAIN_NAME=[domain name]
	repository_name=$(or $(REPOSITORY_NAME), $(PROJECT_ID))
	make aws-codeartifact-crate-domain ||:
	# public:npmjs
	make aws-codeartifact-create-repository REPOSITORY_NAME=$${repository_name}-npmjs-upstream ||:
	make aws-codeartifact-associate-external-repository REPOSITORY_NAME=$${repository_name}-npmjs-upstream EXTERNAL_NAME=npmjs ||:
	# public:pypi
	make aws-codeartifact-create-repository REPOSITORY_NAME=$${repository_name}-pypi-upstream ||:
	make aws-codeartifact-associate-external-repository REPOSITORY_NAME=$${repository_name}-pypi-upstream EXTERNAL_NAME=pypi ||:
	# public:maven-central
	make aws-codeartifact-create-repository REPOSITORY_NAME=$${repository_name}-maven-central-upstream ||:
	make aws-codeartifact-associate-external-repository REPOSITORY_NAME=$${repository_name}-maven-central-upstream EXTERNAL_NAME=maven-central ||:
	# project
	make aws-codeartifact-create-repository \
		REPOSITORY_NAME=$$repository_name \
		UPSTREAMS="repositoryName=$${repository_name}-npmjs-upstream repositoryName=$${repository_name}-pypi-upstream repositoryName=$${repository_name}-maven-central-upstream"

aws-codeartifact-config-npm: ### Configure npm client to use CodeArtifact - mandatory: REPOSITORY_NAME=[repository name]; optional: DOMAIN_NAME=[domain name]
	domain_name=$(or $(DOMAIN_NAME), $(ORG_NAME))
	token=$$(make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) codeartifact get-authorization-token --domain $$domain_name --domain-owner $(AWS_ACCOUNT_ID_MGMT) --region $(AWS_ALTERNATIVE_REGION) --query authorizationToken --output text \
	")
	echo registry=https://$$domain_name-$(AWS_ACCOUNT_ID_MGMT).d.codeartifact.$(AWS_ALTERNATIVE_REGION).amazonaws.com/npm/$(REPOSITORY_NAME)/ > $(TMP_DIR)/.npmrc
	echo //$$domain_name-$(AWS_ACCOUNT_ID_MGMT).d.codeartifact.$(AWS_ALTERNATIVE_REGION).amazonaws.com/npm/$(REPOSITORY_NAME)/:always-auth=true >> $(TMP_DIR)/.npmrc
	echo //$$domain_name-$(AWS_ACCOUNT_ID_MGMT).d.codeartifact.$(AWS_ALTERNATIVE_REGION).amazonaws.com/npm/$(REPOSITORY_NAME)/:_authToken=$$token >> $(TMP_DIR)/.npmrc

# ==============================================================================

# make aws-iam-policy-create NAME=dan-policy DESCRIPTION=test FILE=build/automation/lib/aws/elasticsearch-s3-snapshot-policy-template.json BUCKET=uec-tools-make-devops-jenkins-workspace
# make aws-iam-role-create NAME=dan-role DESCRIPTION=test FILE=build/automation/lib/aws/elasticsearch-s3-snapshot-role.json
# make aws-iam-role-attach-policy ROLE_NAME=dan-role POLICY_NAME=dan-policy
# aws sts assume-role --role-arn arn:aws:iam::$AWS_ACCOUNT_ID:role/dan-role --role-session-name dan-test
# make aws-elasticsearch-create-snapshot DOMAIN=sf1-nonprod BUCKET=uec-tools-make-devops-jenkins-workspace IAM_ROLE=dan-role

aws-elasticsearch-create-snapshot: ### Create an Elasticsearch snapshot - mandatory: DOMAIN=[Elasticsearch domain name],SNAPSHOT_NAME
	endpoint=$$(make aws-elasticsearch-get-endpoint DOMAIN=$(DOMAIN))
	make _aws-elasticsearch-register-snapshot-repository ENDPOINT="$$endpoint"
	#curl -XPUT "https://$$endpoint/_snapshot/snapshot-repository-$(DOMAIN)/$(SNAPSHOT_NAME)"

aws-elasticsearch-get-endpoint: ### Get Elasticsearch endpoint - mandatory: DOMAIN=[Elasticsearch domain name]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) es describe-elasticsearch-domain \
			--domain-name $(DOMAIN) \
			--region $(AWS_REGION) \
			--query 'DomainStatus.Endpoints.vpc' \
			--output text \
	" | tr -d '\r' | tr -d '\n'

_aws-elasticsearch-register-snapshot-repository: ### Register Elasticsearch snapshot repository - mandatory: ENDPOINT,BUCKET,IAM_ROLE
	json='{"type":"s3","settings":{"bucket":"$(BUCKET)","region":"$(AWS_REGION)","role_arn":"arn:aws:iam::$(AWS_ACCOUNT_ID):role/$(IAM_ROLE)"}}'
	curl -X PUT https://$(ENDPOINT)/_snapshot/dan-role?verify=false -d '{"type":"s3","settings":{"bucket":"$(BUCKET)","region":"$(AWS_REGION)","role_arn":"arn:aws:iam::$(AWS_ACCOUNT_ID):role/$(IAM_ROLE)"}}'
	# make -s docker-run-tools \
	# 	DIR=build/docker/elastic-search-backup/assets/scripts \
	# 	SH=y CMD=" \
	# 		pip install requests-aws4auth && \
	# 		python register-es-repo.py \
	# 			$(ES_ENDPOINT) \
	# 			$(AWS_ACCOUNT_ID) \
	# 			snapshot-repo-$(PROFILE) \
	# 			$(TF_VAR_es_snapshot_bucket) \
	# 			$(TF_VAR_es_snapshot_role) \
	# 	"

# ==============================================================================

aws-accounts-setup: ### Ask user to input valid AWS account IDs to be used by the DevOps automation toolchain scripts
	file=$(DEV_OHMYZSH_DIR)/plugins/$(DEVOPS_PROJECT_NAME)/aws-platform.zsh
	mgmt_id=$$(cat $$file | grep "export AWS_ACCOUNT_ID_MGMT=" | sed "s/export AWS_ACCOUNT_ID_MGMT=//")
	nonprod_id=$$(cat $$file | grep "export AWS_ACCOUNT_ID_NONPROD=" | sed "s/export AWS_ACCOUNT_ID_NONPROD=//")
	prod_id=$$(cat $$file | grep "export AWS_ACCOUNT_ID_PROD=" | sed "s/export AWS_ACCOUNT_ID_PROD=//")
	parent_id=$$(cat $$file | grep "export AWS_ACCOUNT_ID_LIVE_PARENT=" | sed "s/export AWS_ACCOUNT_ID_LIVE_PARENT=//")
	identities_id=$$(cat $$file | grep "export AWS_ACCOUNT_ID_IDENTITIES=" | sed "s/export AWS_ACCOUNT_ID_IDENTITIES=//")
	printf "\nPlease, provide valid AWS account IDs or press ENTER to leave it unchanged.\n\n"
	read -p "AWS_ACCOUNT_ID_MGMT        ($$mgmt_id) : " new_mgmt_id
	read -p "AWS_ACCOUNT_ID_NONPROD     ($$nonprod_id) : " new_nonprod_id
	read -p "AWS_ACCOUNT_ID_PROD        ($$prod_id) : " new_prod_id
	read -p "AWS_ACCOUNT_ID_LIVE_PARENT ($$parent_id) : " new_parent_id
	read -p "AWS_ACCOUNT_ID_IDENTITIES  ($$identities_id) : " new_identities_id
	make aws-accounts-create-template-config-file-v1
	if [ -n "$$new_mgmt_id" ]; then
		make -s file-replace-content \
			FILE=$$file \
			OLD="export AWS_ACCOUNT_ID_MGMT=$$mgmt_id" \
			NEW="export AWS_ACCOUNT_ID_MGMT=$$new_mgmt_id" \
		> /dev/null 2>&1
	fi
	if [ -n "$$new_nonprod_id" ]; then
		make -s file-replace-content \
			FILE=$$file \
			OLD="export AWS_ACCOUNT_ID_NONPROD=$$nonprod_id" \
			NEW="export AWS_ACCOUNT_ID_NONPROD=$$new_nonprod_id" \
		> /dev/null 2>&1
	fi
	if [ -n "$$new_prod_id" ]; then
		make -s file-replace-content \
			FILE=$$file \
			OLD="export AWS_ACCOUNT_ID_PROD=$$prod_id" \
			NEW="export AWS_ACCOUNT_ID_PROD=$$new_prod_id" \
		> /dev/null 2>&1
	fi
	if [ -n "$$new_parent_id" ]; then
		make -s file-replace-content \
			FILE=$$file \
			OLD="export AWS_ACCOUNT_ID_LIVE_PARENT=$$parent_id" \
			NEW="export AWS_ACCOUNT_ID_LIVE_PARENT=$$new_parent_id" \
		> /dev/null 2>&1
	fi
	if [ -n "$$new_identities_id" ]; then
		make -s file-replace-content \
			FILE=$$file \
			OLD="export AWS_ACCOUNT_ID_IDENTITIES=$$identities_id" \
			NEW="export AWS_ACCOUNT_ID_IDENTITIES=$$new_identities_id" \
		> /dev/null 2>&1
	fi
	printf "\nFILE: $$file\n"
	tput setaf 4
	cat $$file
	tput setaf 2
	printf "Please, run \`reload\` to make sure that this change takes effect!\n\n"
	tput sgr0

aws-accounts-create-template-config-file-v1: ### Create AWS accounts variables template config file for Texas v1
	(
		echo
		echo "# export: AWS platform variables"
		echo "export AWS_ACCOUNT_ID_MGMT=000000000000"
		echo "export AWS_ACCOUNT_ID_NONPROD=000000000000"
		echo "export AWS_ACCOUNT_ID_PROD=000000000000"
		echo "export AWS_ACCOUNT_ID_LIVE_PARENT=000000000000"
		echo "export AWS_ACCOUNT_ID_IDENTITIES=000000000000"
		echo
		echo "# export: Texas platform variables"
		echo "export TEXAS_TLD_NAME=example.uk"
		echo
	) > $(DEV_OHMYZSH_DIR)/plugins/$(DEVOPS_PROJECT_NAME)/aws-platform.zsh

# ==============================================================================

.SILENT: \
	aws-account-check-id \
	aws-account-get-id \
	aws-accounts-create-template-config-file-v1 \
	aws-accounts-setup \
	aws-assume-role-export-variables \
	aws-cognito-get-client-id \
	aws-cognito-get-client-secret \
	aws-cognito-get-userpool-id \
	aws-dynamodb-exists \
	aws-dynamodb-query \
	aws-ecr-get-image-digest \
	aws-ecr-get-login-password \
	aws-elasticsearch-get-endpoint \
	aws-iam-policy-exists \
	aws-iam-role-exists \
	aws-rds-describe-instance \
	aws-rds-get-snapshot-status \
	aws-s3-exists \
	aws-secret-create \
	aws-secret-exists \
	aws-secret-get \
	aws-secret-get-and-format \
	aws-secret-put \
	aws-user-get-role
