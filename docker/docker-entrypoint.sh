#!/bin/bash

# http://linuxcommand.org/lc3_man_pages/seth.html 
set -eo pipefail

shopt -s nullglob

# check to see if this file is being run or sourced from another script
_is_sourced() {
	# https://unix.stackexchange.com/a/215279
	[ "${#FUNCNAME[@]}" -ge 2 ] \
		&& [ "${FUNCNAME[0]}" = '_is_sourced' ] \
		&& [ "${FUNCNAME[1]}" = 'source' ]

}

# logging functions
log_log() {
	local type="$1"; shift
	printf '%s [%s] [Entrypoint]: %s\n' "$(date --rfc-3339=seconds)" "$type" "$*"
}
log_note() {
	log_log Note "$@"
}
log_error() {
	log_log Error "$@"
}

_migrate() {
	log_note "Migrating apps to the database"
	python "$PWD/manage.py" migrate --noinput >&1 2>&2
}

_main() {
	if [ $1 = "--migrate" ]; then
		shift
		_migrate
	fi


	log_note "Executing $@"
    exec "$@" >&1
}

# If we are sourced from elsewhere, don't perform any further actions
if ! _is_sourced; then
	_main "$@"
fi
