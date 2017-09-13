#!/usr/bin/env bash

source "$(dirname ${BASH_SOURCE[0]})/utils.sh"

PGDATABASE=test_db

ensure "build image" docker-compose build server
ensure "kill server " docker-compose kill server
ensure "rm server " docker-compose rm -f server
ensure "setup service" docker-compose up -d server db
waituntil 10 "connect postgres" docker-compose exec db pg_isready
docker-compose exec db dropdb ${PGDATABASE} -U postgres
ensure "create db" docker-compose exec db createdb ${PGDATABASE} -U postgres
ensure "init db" docker-compose run --rm -e dbname=${PGDATABASE} server python -m service.migrations
ensure "running coverage erase" docker-compose run --rm -e dbname=${PGDATABASE} server coverage erase
ensure "running coverage run" docker-compose run --rm -e dbname=${PGDATABASE} server coverage run --source service -m ethicall_common service.tests
ensure "running coverage xml" docker-compose run --rm -e dbname=${PGDATABASE} server coverage xml -o reports/coverage.xml
ensure "running coverage2clover" docker-compose run --rm -e dbname=${PGDATABASE} server coverage2clover -i reports/coverage.xml -o reports/clover.xml
ensure "running coverage html" docker-compose run --rm -e dbname=${PGDATABASE} server coverage html -d reports
