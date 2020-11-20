Copyright 2017-2020 DMTF. All rights reserved.

# YANG to Redfish CSDL Converter tool

## Introduction

This converter tool is used to converter a YANG schema file into a Redfile CSDL schema file. The resulting file can be placed in the ./metadata folder.

The conversion is done in accordance with the [YANG to Redfish Mapping Specification](https://www.dmtf.org/sites/default/files/standards/documents/DSP0271_0.5.6.pdf).

## Pre-requisites

The converter tool is constructed as a pyang plugin. The Python code executes in **Python 3.x.**.

To execute the converter tool, the following python modules should be installed.

* lxml
* pyang

## Generating a Redfish schema file from a YANG schema file

The process is composed of two steps

1. Obtain a YANG schema file
2. Execute this converter

## Execute the YANG-to-Redfish Converter

The following command performs the conversion:

    pyang --plugindir ./YANG-to-Redfish-Plugin --format redfish <yang-file>

Multiple YANG schema files can be placed on the command line:
    
    pyang --plugindir ./YANG-to-Redfish-Plugin --format redfish <yang-file1> <yang-file2> <yang-file3> <...>

The following command line parameters are supported:

* --target\_dir
* --format
* --plugindir
* --remove\_cyclical\_imports
* --combine\_all\_nodes

The **--target\_dir** parameter specifies the folder in which resultant Redfish CSDL is placed.  If the parameter is not on the command line, the folder **output\_dir** is used.

The **--format** parameter specifies the format of the conversion. Currently, only **redfish** is recognized.

The **--plubindir** parameter specifies the plugin to use with pyang.

The **--remove\_cyclical\_imports** parameter specifies ...

The **--combine\_all\_nodes** parameter specifies whether the entity types are placed in a single YANG schema file or placed in separate YANG schema files.

The command line used to general the Redfish schema files in the work-in-progress is:

    pyang --plugindir ./YANG-to-Redfish-Plugin --format redfish --target_dir testdir --combine_all_nodes <yang-file>
    
Upon completion, the tool will display the message

    Success writing file to disk: output_dir/openconfig_acl_v1.xml

**Note** The tool displays the following message, which is informational.

    We don't recognize keyword ('openconfig-extensions', 'openconfig-version'), create as statement

## Obtaining a YANG schema file

A YANG schema file contains the text between <CODE BEGINS\> and <CODE ENDS\> within a YANG RFC file.  There several ways to obtain this file.

* Use the xym tool to extract the YANG schema file from a YANG RFC file
* Download a YANG schema file from the YangModels Github and remove the Byte-Order-Mark

### Extract the YANG schema file from an RFC file

The **xym** tool extracts the YANG code from a YANG file.  If the YANG file contains multiple YANG models, the tool will extract the schema code for each model and placed them in separate files.

1. Install the xym tool, using pip or from its Github repository (github.com/xym-tool/xym)

        pip install xym

2. Download a YANG RFC in text format.  One source of YANG RFC files is **tools.ietf.org**
3. Use the tool to extract the YANG model.  The extracted YANG models will each have a *.yang extensions.

        xym <yang_rfc.txt>

### Download a YANG schema file from the YangModels Github

The **github.com/YangModels**, contains a collection of YANG schema files.

However these files contain a Byte-Order-Mark (BOM) at the front of the file, three special characters. The BOM needs to be removed before the file is used as input into the converter. The BOM can be removed in two ways.

* Use VIM
* Run remove_bom.py

#### Remove Byte-Order-Mark with VIM

When the file is opened with VIM, the BOM can be seen by viewing the file in HEX mode. This is accomplished by using the ":%1xxd" command, or selecting the "Convert to HEX" in the "Tools" tab.

The BOM is removed by using the ":setlocal" command. (The "w" command writes the file.)

    :setlocal nobomb 
    :w

#### Remove Byte-Order-Mark with remove_bom.py

Execute the following remove_bom.py program. The remove_bom.py file is located in the **./src** folder.

    $> cmd /c '.\src\remove_bom.py < [input file] > [output file]'

Note: the 'cmd' is needed in the command because "<" is not recognized by Powershell, but 'cmd' recognizes it.

## Using the Resultant CSDL file

The resulting CSDL files can be placed in the ./metadata folder of the Redfish Service file structure.

##Folder Structure 

The YANG-to-Redfish repository contains three folders:

* src - contains the source code for the converter pyang plugin
* yangs - contains sample YANG schema files that have been successfully converter
* output_dir - contains the resultant Redfish CSDL files

The **yangs** folder also contains the YANG schema files referenced by other YANG schema files.

## Release Process

1. Update `CHANGELOG.md` with the list of changes since the last release
2. TODO: Add version string in the tool somewhere
3. Push changes to Github
4. Create a new release in Github
