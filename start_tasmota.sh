#!/bin/bash
WORKING_DIRECTORY=/opt/tasmota/
cd $WORKING_DIRECTORY
source $WORKING_DIRECTORY/venv/bin/activate
$WORKING_DIRECTORY/venv/bin/python3 $WORKING_DIRECTORY/main.py
