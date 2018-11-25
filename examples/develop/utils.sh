#!/usr/bin/env bash

waituntil () {
  local count=0
  local limit="$1"
  local msg="$2"
  shift 2
  until echo "trying to ${msg} $((count+1))" && "$@"
  do
    count=$((count+1))
    sleep 10

    if [ "$count" -ge "$limit" ]
    then
       echo "failed to ${msg}"
       exit 1
    fi
  done
}

ensure () {
  local msg="$1"
  shift
  echo "${msg}"
  "$@" || exit 1
}
