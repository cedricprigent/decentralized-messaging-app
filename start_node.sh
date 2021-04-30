#!/bin/bash
python 'run_app.py'&
addr=`python -c "import network_details; addr = network_details.get_ip_address_2(); cmd = \"flask run -h \"+addr+\" --port 8000\"; print(cmd)"`
bash -c `$addr`
