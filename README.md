Copyright 2017-2018 Distributed Management Task Force, Inc. All rights reserved.

# YANG to Redfish CSDL Converter tool

## Introduction

This pyang plugin converts a YANG model file to a set of corresponding Redfish OData CSDL files.

The conversion is done in accordance with the [YANG to Redfish Mapping Specification](https://www.dmtf.org/sites/default/files/standards/documents/DSP0271_0.5.6.pdf).
Per the specification, a single YANG model can result in multiple CSDL files being generated. 

The Python code executes in **Python 3.x.**.

## Pre-requisites

The following modules should be installed.

* lxml
* pyang

## Folder Structure 

The code is organized in the following folder structure:

    root
    - YANG-to-Redfish-Plugin

 - **YANG-to-Redfish-Plugin:** This is the top level directory containing all the source files.

## Process

The process is composed of two steps

1. Obtain a YANG code file
2. Execute **pyang** with this plugin to generate the Redfish CSDL files

## How to run the plugin

Given an obtained set of YANG files, you can run the plugin in the following way:

    pyang --plugindir ./YANG-to-Redfish-Plugin --format redfish <path-to-file>

By default, the resultant Redfish CSDL files are place in the directory **output\_dir**. The paramenter **--target\_dir** can be used to specify the output directory.

    pyang --plugindir ./YANG-to-Redfish-Plugin --format redfish --target_dir testdir <path-to-file>

## Obtain a YANG code file

The YANG code file contains the text between <CODE BEGINS\> and <CODE ENDS\> within a YANG RFC file.  There several ways to obtain this file.

* Use the xym tool to extract the YANG code from a YANG RFC file
* Download a YANG code file from the YangModels Github and remove the BOM
* Manually edit a YANG RFC file

### Use xym to extract YANG code file

The **xym** tool extracts the YANG code from a YANG file.  If the YANG file contains multiple YANG models, the code for each model will be extracted and placed in separate files.

1. Install the xym tool, using pip or from its Github repository (github.com/xym-tool/xym)

        pip install xym

2. Download a YANG RFC in text format.  One source of YANG RFC files is **tools.ietf.org**
3. Use the tool to extract the YANG model.  The extracted YANG models will each have a *.yang extensions.

        xym <yang_rfc.txt>

### Download a YANG code file from the YangModels Github

* The **github.com/YangModels**, contains a collection of YANG code files.
* However the files contain a Byte-Order-Mark at the front of the file. The BOM is three special characters and needs to be removed before the file is used as input into the converter.
* The BOM can be removed in two ways
    * Use VIM
    * Run remove_bom.py

#### Remove BOM with VIM

Open the file with VIM and enter the following commands.  Then save and exit the file.

    :setlocal nobomb 
    :w

#### Remove BOM with remove_bom.py

Execute the following command.

    $> cmd /c '.\src\remove_bom.py < [input file] > [output file]'

The remove_bom.py file is located in the directory **src**.

Note: the 'cmd' is needed in the command because "<" is not recognized by Powershell, but 'cmd' recognizes it.
