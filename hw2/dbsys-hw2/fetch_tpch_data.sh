#!/bin/bash
# Usage sh fetch_new_data.sh 0.01 or 0.1
rm -rf data/ ; cp -r /home/cs416/datasets/tpch-hw2/data-tpch-sf-"$1"/data-tpch-sf"$1"/ . ; mv data-tpch-sf"$1" data