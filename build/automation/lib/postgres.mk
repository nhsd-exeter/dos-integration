POSTGRES_VERSION_MAJOR = 13
POSTGRES_VERSION_MINOR = 3
POSTGRES_VERSION = $(POSTGRES_VERSION_MAJOR).$(POSTGRES_VERSION_MINOR)
AWS_POSTGRES_VERSION_MAJOR = 12
AWS_POSTGRES_VERSION_MINOR = 4
AWS_POSTGRES_VERSION = $(AWS_POSTGRES_VERSION_MAJOR).$(AWS_POSTGRES_VERSION_MINOR)

postgres-check-versions: ### Check PostgreSQL versions alignment
	echo "postgres library: $(POSTGRES_VERSION) (current $(DEVOPS_PROJECT_VERSION))"
	echo "postgres library aws: $(AWS_POSTGRES_VERSION) (current $(DEVOPS_PROJECT_VERSION))"
	echo "postgres virtual: none"
	echo "postgres docker: $$(make docker-repo-list-tags REPO=postgres | grep -w "^[0-9]*\(\.[0-9]*\(\.[0-9]*\)\?\)\?-alpine$$" | sort -V -r | head -n 1 | sed "s/-alpine//g" | sed "s/^[[:space:]]*//g") (latest)"
	echo "postgres aws: unknown"

.SILENT: \
	postgres-check-versions
