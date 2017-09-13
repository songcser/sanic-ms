#!/usr/bin/env bash

source "$(dirname $(readlink -f ${BASH_SOURCE[0]}))/utils.sh"
waituntil 10 "connect postgres" pg_isready -h db -d postgres
waituntil 10 "connect server" curl -vvv 'http://server:8000/'
