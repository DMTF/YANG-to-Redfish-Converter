# Change Log

## [1.0.4] - 2020-10-19
- Many enhancements and fixes over the last year of testing

## [1.0.3] - 2019-03-01
- Added fixes to the plugin that resolves resolution issues when generating multiple CSDL files
- Removed generation of groupings/uses statements, as they're definitions but not resources
- Resolved typing resolutions for enumerations in groupings

## [1.0.2] - 2018-11-30
- Updates to the tool based on feedback from test tools that verify schema format
- Moved repeated annotations into collections of annotations
- Added uses/groups support
- Added options for single file generation and avoiding cyclical imports
- Type resolution no longer dependent on exporting CSDL Type enums to RedfishYangExtensions, but to their responsible file

## [1.0.1] - 2018-04-03
- Restructured tool to leverage the pyang module

## [1.0.0] - 2017-10-19
- Initial Release

