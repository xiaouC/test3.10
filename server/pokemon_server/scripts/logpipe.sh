#!/bin/bash

logdir="log"
while read line;do
    if [[ $line =~ \<\<([[:print:]]+)\>\>[[:space:]](.*) ]]; then
        logto="${BASH_REMATCH[1]}"
        each="${BASH_REMATCH[2]}"
        echo $each >> "$logdir/$logto"
    fi
done
