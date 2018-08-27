#!/usr/bin/env bash
mkdir data
cd data
wget http://api.bitcoincharts.com/v1/csv/coinbaseUSD.csv.gz
gunzip coinbaseUSD.csv.gz