#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Usage: $1 <install|run>"
    exit
fi

if [[ $1 == "install" ]]; then
    echo "Compiling.."
    g++ -DUNIX -g -o caen_sy5527 -O2 -lcaenhvwrapper -lpthread -ldl caen_sy5527.cpp
    if [[ $? -ne 0 ]]; then
        echo "Do you have the appropriate libraries?"
    else
        echo "Success"
    fi
elif [[ $1 == "run" ]]; then
    ./caen_sy5527 5000 192.168.131.12
fi
