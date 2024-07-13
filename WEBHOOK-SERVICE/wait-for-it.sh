#!/usr/bin/env bash
#   Use this script to test if a given TCP host/port are available

WAITFORIT_cmdname=${0##*/}

echoerr() { if [[ $WAITFORIT_QUIET -ne 1 ]]; then echo "$@" 1>&2; fi }

usage() {
    exitcode="$1"
    cat << USAGE >&2
Usage:
    $WAITFORIT_cmdname host:port [-s] [-t timeout] [-- command args]
    -h HOST | --host=HOST       Host or IP under test
    -p PORT | --port=PORT       TCP port under test
                                Alternatively, you specify the host and port as host:port
    -s | --strict               Only execute subcommand if the test succeeds
    -q | --quiet                Don't output any status messages
    -t TIMEOUT | --timeout=TIMEOUT
                                Timeout in seconds, zero for no timeout
    -- COMMAND ARGS             Execute command with args after the test finishes
USAGE
    exit "$exitcode"
}

wait_for() {
    if [[ $WAITFORIT_TIMEOUT -gt 0 ]]; then
        echoerr "$WAITFORIT_cmdname: waiting $WAITFORIT_TIMEOUT seconds for $WAITFORIT_HOST:$WAITFORIT_PORT"
    else
        echoerr "$WAITFORIT_cmdname: waiting for $WAITFORIT_HOST:$WAITFORIT_PORT without a timeout"
    fi
    WAITFORIT_start_ts=$(date +%s)
    while :
    do
        if [[ $WAITFORIT_ISBUSY -eq 1 ]]; then
            nc -z "$WAITFORIT_HOST" "$WAITFORIT_PORT"
            WAITFORIT_result=$?
        else
            (echo > /dev/tcp/"$WAITFORIT_HOST"/"$WAITFORIT_PORT") >/dev/null 2>&1
            WAITFORIT_result=$?
        fi
        if [[ $WAITFORIT_result -eq 0 ]]; then
            WAITFORIT_end_ts=$(date +%s)
            echoerr "$WAITFORIT_cmdname: $WAITFORIT_HOST:$WAITFORIT_PORT is available after $((WAITFORIT_end_ts - WAITFORIT_start_ts)) seconds"
            break
        fi
        sleep 1
    done
    return $WAITFORIT_result
}

WAITFORIT_hostport=""
WAITFORIT_hostport="$1"
shift

if [[ "$WAITFORIT_hostport" == *:* ]]; then
    WAITFORIT_HOST=$(printf "%s\n" "$WAITFORIT_hostport" | cut -d : -f 1)
    WAITFORIT_PORT=$(printf "%s\n" "$WAITFORIT_hostport" | cut -d : -f 2)
else
    WAITFORIT_HOST="$WAITFORIT_hostport"
    WAITFORIT_PORT="$2"
    shift
fi

WAITFORIT_TIMEOUT=15
WAITFORIT_STRICT=0
WAITFORIT_QUIET=0
WAITFORIT_ISBUSY=0

while [[ $# -gt 0 ]]
do
    case "$1" in
        *:*)
        WAITFORIT_hostport="$1"
        WAITFORIT_HOST=$(printf "%s\n" "$WAITFORIT_hostport" | cut -d : -f 1)
        WAITFORIT_PORT=$(printf "%s\n" "$WAITFORIT_hostport" | cut -d : -f 2)
        shift 1
        ;;
        -q | --quiet)
        WAITFORIT_QUIET=1
        shift 1
        ;;
        -s | --strict)
        WAITFORIT_STRICT=1
        shift 1
        ;;
        -h)
        WAITFORIT_HOST="$2"
        if [[ $WAITFORIT_HOST == "" ]]; then break; fi
        shift 2
        ;;
        --host=*)
        WAITFORIT_HOST=$(printf "%s\n" "$1" | cut -d = -f 2)
        shift 1
        ;;
        -p)
        WAITFORIT_PORT="$2"
        if [[ $WAITFORIT_PORT == "" ]]; then break; fi
        shift 2
        ;;
        --port=*)
        WAITFORIT_PORT=$(printf "%s\n" "$1" | cut -d = -f 2)
        shift 1
        ;;
        -t)
        WAITFORIT_TIMEOUT="$2"
        if [[ $WAITFORIT_TIMEOUT == "" ]]; then break; fi
        shift 2
        ;;
        --timeout=*)
        WAITFORIT_TIMEOUT=$(printf "%s\n" "$1" | cut -d = -f 2)
        shift 1
        ;;
        --)
        shift
        WAITFORIT_CLI=("$@")
        break
        ;;
        --help)
        usage 0
        ;;
        *)
        echoerr "Unknown argument: $1"
        usage 1
        ;;
    esac
done

if [[ "$WAITFORIT_HOST" == "" || "$WAITFORIT_PORT" == "" ]]; then
    echoerr "Error: you need to provide a host and port to test."
    usage 2
fi

wait_for

WAITFORIT_result=$?

if [[ $WAITFORIT_CLI != "" ]]; then
    if [[ $WAITFORIT_result -ne 0 && $WAITFORIT_STRICT -eq 1 ]]; then
        echoerr "$WAITFORIT_cmdname: strict mode, refusing to execute subprocess"
        exit $WAITFORIT_result
    fi
    exec "${WAITFORIT_CLI[@]}"
else
    exit $WAITFORIT_result
fi
