Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.

# Yang to CSDL Converter tool

## Introduction

This tool converts a YANG model file to the corresponding Redfish schema, specified in OData CSDL. The conversion is done in accordance with the YANG-to-CSDL Mapping Specification.

A single YANG model could result in multiple CSDL XML output files being generated. 

The Python code executes in **Python 3.x.**

## Folder Structure 

The code is organized in the following folder structure:

    root
    - src
    - yangs_bom
    - yangs_raw
    - yangs
    - csdl

 - **src:** This is the top level directory containing all the source files. See HACKING.md for details.
 - **yangs:** This folder is used to to place YANG models which have been successfully used as  input into the converter (i.e. known to work).  Note, some editing may have been performed on the raw YANG model to circumvent converted issues.
 - **yangs_raw:** This folder is used to place YANG models which reflect the RFC version. The files may may work on the converter, since some statements may not be recognized.
 - **yangs_bom:** This folder is used to place YANG models downloaded from **github.com/YangModels**, with the 'Save As" operation. Files downloaded with 'Save As" operation have a byte-order-marker (BOM). This BOM must be remove in order for the file can be used as input into the converter.
 - **csdl:** This folder is used to place the output of the conversion.  The names of the subfolders are specified as a parameter passed to the converter.  These file can be copied directly into ./metadata. 

## Process

The process is composed of two steps

1. Obtain a YANG code file
2. Use this converter to generate the Redfish CSDL files

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

## Generate the Redfish CSDL files

The following shows how this tool is used the generate the Redfish CSDL files.
 
	$python yang_to_csdl_tool.py --input yangs/yang_input.yang --output-dir csdl/ --verbose info

### Manpage for yang\_to\_csdl_tool.py

The **yang\_to\_csdl\_tool.py** generates Redfish CSDL files by converting the statements in the YANG code file. Below is the general format of the command

	$python yang_to_csdl_tool.py [options]

### Options

	--help           : Show help text & exit
	--input          : Path to the input YANG model 
	--verbose        : Set logging verbosity (debug, info, error, warning, critical) 
	--output-dir     : Path to directory to store CSDL output files
	--output-grammar : Output YANG parsing grammar on console (Academic interest only)
	--version        : Print version information and exit

Verbose: Messages with level >= the set level will be logged. Valid values are debug, info, error, warning, and critical. Default log level is set to error if verbosity is not set from command line.

## Installation

The installation of binaries are necessary to support two executables: yang\_to\_csdl_tool.py and postprocess.sh.

### Tools required by yang\_to\_csdl_tool.py

Install the Python package, modgrammar.

		/python27/scripts/pip.exe install modgrammar

### Tools required by postprocess.sh

The postprocess.sh requires **xmllint**.  The installation of this tool for Windows and Linux are different.

For Windows, go to the [Link](https://www.zlatkovic.com/libxml.en.html) and click on **download area**. For each of the four zip files, copy the contents from the ./bin directory to a directory in the PATH environment variable.  Note: the bin directory of libxml2 contains xmllint.exe.

* iconv
* libxml2
* libxslt
* zlib

For Linux, xmllint is a simple copy.  This tool has been tested on Ubuntu 14.04 LTS.

## Supported YANG statements

The following YANG statements are supported. **Note** that even
within this, certain constructs might not be fully supported.

* Module
* Yang version 
* Revision, Reference
* Prefix
* Name, Description
* Namespace
* Feature
* If feature
* Import, Include
* Organization
* Contact 
* Description 
* Choice-Case
* Rpc-Input-Output
* Container
* List
* Leaf & Leaf list
* Typedef
* Type   
* Range, Length, Bits, Min, Max, Path, Base
* Enumeration 
* Config 
* Default 
* Mandatory
* Unique
* Identity
* Status
* Presence
* Must
* Ordered-By
* Grouping (logs message to logfile)
* Uses (logs message to logfile)
* Min-Elements
* Max-Elements
* Deviation, Deviate
* Augment
* Anyxml
* Notification
* Submodule (logs message to logfile)
* Extension, Argument 

## Known Issues

1. Yang files cannot have comments. Comment lines will result a parse error.
	* Remove all "/*** ... ***/" lines
2. The converter cannot handle single quotes ('). Change single quotes (') to double quotes ("). For example:
	* leaf "server" {blah} - OK
	* leaf 'server' {blah} - Will result  in parse error
3. Use of the extended statement (i.e the target of the extension statement) in the grammar is not supported
4. The converter has been tested on existing Yang files. There may be YANG statement constructs which have not been used so far. For example: a reference statement within leaf statement). If such constructs are encountered, then the tool will need to be modified.

## Hacking

To understand the source code and how the modify and contribute, see the HACKING.md file.
