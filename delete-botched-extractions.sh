#!/bin/sh -ex

root=$(dirname $0)

find $root/*/ -type f -size 0 -delete
find $root/apkanalyzer-dex-packages/ -type f -name \*.dex-dump.gz -size -1000c  -delete
find $root/apkparser-axml2xml/ -type f -name \*.AndroidManifest.xml -size -100c -delete
find $root/unzip-faup/ -type f -name \*.unzip-faup.csv -size -50c -delete
