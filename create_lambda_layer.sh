#!/bin/bash

pip3.7 install -t python/lib/python3.7/site-packages duckdb
zip -r lambda_layers/duckdb.zip python
rm -r python