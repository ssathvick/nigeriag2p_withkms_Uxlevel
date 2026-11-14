#!/bin/bash

input_file=$1
output_file=$2

while read line; do
    # Skip empty lines and comments
    if [[ -z "$line" ]] || [[ "$line" =~ ^# ]]; then
        echo "$line" >> $output_file
        continue
    fi

    key=$(echo "$line" | cut -d'=' -f1)
    echo "$key=/@$key@" >> $output_file
done < $input_file
