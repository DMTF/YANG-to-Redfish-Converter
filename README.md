Copyright 2017-2018 Distributed Management Task Force, Inc. All rights reserved.

# Yang to CSDL Converter tool

## Introduction

This plugin converts a YANG model file to the corresponding Redfish schema, specified in OData CSDL. The conversion is done in accordance with the YANG-to-CSDL Mapping Specification.

A single YANG model could result in multiple CSDL XML output files being generated. 

The Python code executes in **Python 3.x.**, and utilizes the program pyang

## Pre-requisites

Python 3 is required for this program, along with the following library:
* pyang

The above can be installed through the pip3 command line tool

## Folder Structure 

The code is organized in the following folder structure:

    root
    - YANG-to-Redfish-Plugin

 - **YANG-to-Redfish-Plugin:** This is the top level directory containing all the source files.

## Process

The process is composed of two steps

1. Obtain a YANG code file, via official files or from RFC files.
2. Use this plugin to generate the Redfish CSDL files

## How to run the plugin

Given an obtained set of YANG files, you can run the plugin in the following way:

* run the following: pyang --plugindir ./YANG-to-Redfish-Plugin --format redfish <path-to-file>

Along with the parameters for pyang, the plugin has the following independent parameters:

* --target-dir :  where to output the xml files, default './output_dir'

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
* Using VIM, open the file and enter the following commands.

        	:setlocal nobomb 
        	:w
* Using ./src/remove_bom.py, issue the following command. Note: the 'cmd' is needed in the command because "<" is not recognized by Powershell. The above command places the resultant YANG code file into the ./yangs directory.

			$> cmd /c '.\src\remove_bom.py < yangs_bom/[input file] > yangs/[output file]'

2. Execute the yang_to_csdl_tool.yang to convert the file. The **--input** option specifies a YANG code file.  The **--output-dir** option specifies the directory for the resultant CSDL. The directory name should include the backslash.

		$> python src/yang_to_csdl_tool.py --input yangs/input.yang --output-dir csdl/rfc1234

3. Execute the postprocess shell script to beautify the resultant CSDL.  While this command runs, you will see a blank command window will pop up. When the command completes, the command window will disappear.

		$> .\src\postprocess.sh csdl/rfc1234


