#!/usr/bin/python
# Copyright Notice:
# Copyright 2017 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/YANG-to-Redfish-Converter/blob/master/LICENSE.md

import codecs
import shutil
import sys

s = sys.stdin.read(3)
if s != codecs.BOM_UTF8:
    sys.stdout.write(s)

shutil.copyfileobj(sys.stdin, sys.stdout)
