#!/bin/bash
source bin/activate
pip3 install -r requirements.txt
python3 -mdownloader "$@"
