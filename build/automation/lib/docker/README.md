# Docker

## General

Build script functionality

- Pre-defined directory structure
- Source code provided as an archive for a transparent and consistent build process
- Self-signed SSL certificate to ensure traffic is encrypted in transit
- Metadata variables and labels populated with the image build details
- Template-based versioning
- `goss` tests

## Library images

Some of the benefits of using the library images

- Alpine-based images
- Locale and timezone set accordingly to the location
- `bash`, `curl` and `gosu` commands included
- `entrypoint`, `wait-for-it`, `init` and `run` scripts
- `prepare_configuration_files`, `replace_variables` and `set_file_permissions` functions
- Process debugging and tracing functionality
- Support to run process as a non-root system user

## Template images

- Usage examples
- Health check included

## TODO

- Convert examples to templates
- Remove python-app or convert it to a template

## Status

| Category                     | Badges                                                                                                                                                                                                                                                      |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Docker `elasticsearch` image | [![version](https://img.shields.io/docker/v/nhsd/elasticsearch?sort=semver)](https://hub.docker.com/r/nhsd/elasticsearch/tags)&nbsp;[![docker pulls](https://img.shields.io/docker/pulls/nhsd/elasticsearch)](https://hub.docker.com/r/nhsd/elasticsearch/) |
| Docker `nginx` image         | [![version](https://img.shields.io/docker/v/nhsd/nginx?sort=semver)](https://hub.docker.com/r/nhsd/nginx/tags)&nbsp;[![docker pulls](https://img.shields.io/docker/pulls/nhsd/nginx)](https://hub.docker.com/r/nhsd/nginx/)                                 |
| Docker `node` image          | [![version](https://img.shields.io/docker/v/nhsd/node?sort=semver)](https://hub.docker.com/r/nhsd/node/tags)&nbsp;[![docker pulls](https://img.shields.io/docker/pulls/nhsd/node)](https://hub.docker.com/r/nhsd/node/)                                     |
| Docker `pipeline` image      | [![version](https://img.shields.io/docker/v/nhsd/pipeline?sort=semver)](https://hub.docker.com/r/nhsd/pipeline/tags)&nbsp;[![docker pulls](https://img.shields.io/docker/pulls/nhsd/pipeline)](https://hub.docker.com/r/nhsd/pipeline/)                     |
| Docker `postgres` image      | [![version](https://img.shields.io/docker/v/nhsd/postgres?sort=semver)](https://hub.docker.com/r/nhsd/postgres/tags)&nbsp;[![docker pulls](https://img.shields.io/docker/pulls/nhsd/postgres)](https://hub.docker.com/r/nhsd/postgres/)                     |
| Docker `python` image        | [![version](https://img.shields.io/docker/v/nhsd/python?sort=semver)](https://hub.docker.com/r/nhsd/python/tags)&nbsp;[![docker pulls](https://img.shields.io/docker/pulls/nhsd/python)](https://hub.docker.com/r/nhsd/python/)                             |
| Docker `python-app` image    | [![version](https://img.shields.io/docker/v/nhsd/python-app?sort=semver)](https://hub.docker.com/r/nhsd/python-app/tags)&nbsp;[![docker pulls](https://img.shields.io/docker/pulls/nhsd/python-app)](https://hub.docker.com/r/nhsd/python-app/)             |
| Docker `tools` image         | [![version](https://img.shields.io/docker/v/nhsd/tools?sort=semver)](https://hub.docker.com/r/nhsd/tools/tags)&nbsp;[![docker pulls](https://img.shields.io/docker/pulls/nhsd/tools)](https://hub.docker.com/r/nhsd/tools/)                                 |
