#!/bin/bash

source ~/virtual_env/themis/bin/activate
cd ~/work/themis/themis
./manage.py crawl_feeds
