Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# Yang to CSDL - Developer Documentation
----------
The Yang to CSDL convertor converts YANG model file into CSDL model definitions. This document intends to provide a future maintainer with sufficient information to add features and resolve bugs in the code.

## Pre-requisites
This document assumes that the reader is familiar with context free grammar notation. In a context free grammar notation, the productions are a set of recursive rules which generates a pattern of strings. 
The document also assumes that the reader is familiar with Python programming language and the modgrammar library.

## Package Dependencies
The Yang to CSDL tool depends on the python modgrammar package and Python 3.1/3.2. The tool has been tested on Python 3.2 and 3.5.

## Folder Structure 
The code is organized in the following folder structure:

    root
    - src
    - - libs
    - - yang
    - postprocess.sh
    - HACKING.md
    - LICENSE.txt
    - README.md
    - yangs, yangs_bom and csdl

 - src : This is the top level directory containing all the source files.
 - libs : This directory contains python code for file and XML tree operations used within the YANG parsing code.
 - yang: This folder contains the grammar definitions for various yang statements. Please refer to the README.md file for a complete list of supported Yang statements. Note that a statement might be supported only when present in specific containing sections.
 - postprocess.sh - Linux shell script which uses xmllint to pretty-format the CSDL files.
 - \*.md and \*.txt - Self explanatory
 - yangs, yangs_bom and csdl - Folders used as source and target diretory for the conversion.  Different directory names could be used. The usage of these directories are described in the README, which describes the conversion process.

## General program flow
The program flow is fairly straightforward.

- Yang_to_csdl_tool.py is the main routine
	- Handles command line options
	- Calls Module.Grammar to handle the 'module' statement
	- Calls build_tree()

Build\_tree() is recursive function which handles YANG containment statements (e.g. module, container, list, leaf, leaflist). The handlers are defined in statement_handlers.py as <statement>_handler() classes.  These classes call the ./yang/<statement>.py files.

## Supporting a YANG statement
YANG statement grammars are typically defined in a  `<yang_statement>.py` file for each YANG statement type.  However, some files could contain the definitions for multiple statements: 

 1. In some cases, this is to achieve logical containment of yang statements
 2. In some cases, YANG statements have circular definitions - for example a `container` definition allows for `choice` which in turn allows `container` inside it. This leads to import problems in python. Therefore all such statements are defined within a single python source file.

### Adding support for a new YANG statement
Consider a case of adding support for a new YANG statement `foo`. In order to add support for `foo`:

 1. Understand the `foo` statment's YANG defnition to identify possible circular dependencies on existing statements. `foo` might require other new statments (`foo1, foo2...`) whose grammar needs to be defined first.
 2.  Add the grammar definition for `foo` either in an existing source file or in `foo.py`
 3.  Add a `handle_foo` function to handle the statement grammar. Existing `handle_XXX` functions are defined in the `statement_handlers.py` file.
	 1.  This function will typically take the list of grammar elements, current node of XML tree as parameters. Additional parameters might be required in specific cases. 
	 2. The `handle_foo` function would typically not return any value because the XML node that is passed as a parameter is modified to add tags and child nodes as defined by the YANG to CSDL conversion document.
	 3. `handle_foo` could make calls to existing `handle_XXXX` functions.
 4.  The `handle_foo` function must now be called within the `build_tree` function defined in `csdl_tree.py`. `build_tree` is a recursive function which is called by the main function to create the XML tree corresponding to the YANG model.
	 1. The `build_tree`  function takes as parameters, a tree node object (which is used to track the parent-child relationships), the XML node object (to which XML tags are added as child nodes or annotations), the list of grammar elements, a list to which the root node of XML sub-tree is appended, log level, and output directory. The list of XML sub-trees is required because conversion to CSDL results in mulitple CSDL XML files being generated for one YANG input.
 	 2.  The `build_tree` function contains an if-elif-else statement which calls the appropriate `handle_XXX` function.
 	 4. Add a condition for `foo` here and invoke the  `handle_foo` function. This has to be done twice - once in the case of repeating items and once in handling non-repeating items. In the former case, modgrammar will first return a `<REPEAT>` token indicating that the next token must be expanded to get the actual parse tokens.
 	 5. Some `handle_XXX` functions are defined within `csdl_tree.py`  to prevent circular import issues.
 	 6. If `foo` allows any  containment statements - container, leaf, leaf-list, list - then, `handle_foo` will have to call `build_tree`.  


### Modifying existing grammars

Modifying an existing grammar (for example a YANG statement, `bar`) requires two broad changes
1. Editing `bar`'s  grammar in the appropriate source file to address the new statements.
2. Modify the statement handler function to handle the newly added statement. This step might not be necessary if this newly added statement already exists as part of YANG and was missing only in the `bar`'s grammar definition. Else, the steps listed in the previous section should be followed to first support the new statement, followed by modifications to `bar`'s grammar.

## Other functions
The source contains multiple support functions required for XML generation, file handling, command line parsing etc.

- `libs/fileops.py` : Contains convenience functions for file IO.
- `libs/node.py` : Defines the structure of the Node class. This class is used within the parsing to capture the parent-child containment hierarchy.
- `xml_convenience.py` : Defines various functions for commonly used XML operations required during CSDL generation. 
- `xml_content.py` : Defines a class which holds the output filename, and the XML tree which needs to be written to disk. All XML files are written to disk after parsing is completed. 
## References

 1. <link>https://www.cs.rochester.edu/~nelson/courses/csc_173/grammars/cfg.html
 2. <link>https://pypi.python.org/pypi/modgrammar
 3. <link>http://pythonhosted.org/modgrammar/ 
 4. <link>http://www.dmtf.org/sites/default/files/standards/documents/DSP0271_0.5.6.pdf
