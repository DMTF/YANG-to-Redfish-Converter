#!/bin/bash
# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

directory=$1
for file in `ls $directory`; do
	mv $directory/$file $directory/temp.xml 
	xmllint --format $directory/temp.xml 2>/dev/null >$directory/$file 
done
rm $directory/temp.xml
