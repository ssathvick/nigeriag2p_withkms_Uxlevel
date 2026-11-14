#!/bin/bash

WORKDIR="/app"
ENV_FILE=$WORKDIR/.env.prod

IFS=$'\n' next_env_vars=($(awk 'BEGIN{for(v in ENVIRON) print v}' | grep "^NEXT_PUBLIC_"))
for env_var in ${next_env_vars[@]}; do
    file_env_var_line=$(grep "${env_var}=" $ENV_FILE)
    if ! [ -z $file_env_var_line ]; then
        sed -i "s|$file_env_var_line||g" $ENV_FILE
    fi
done

set -a
source $ENV_FILE
set +a

IFS=$'\n' next_env_vars=($(awk 'BEGIN{for(v in ENVIRON) print v}' | grep "^NEXT_PUBLIC_"))
for env_var in ${next_env_vars[@]}; do
    for file in $(find $WORKDIR -name "node_modules" -prune -o -type f -exec grep -l "/@$env_var@" {} \;); do
        sed -i "s|/@$env_var@|${!env_var}|g" $file
    done
done

exec "$@"
