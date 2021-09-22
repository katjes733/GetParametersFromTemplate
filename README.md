# GetParametersFromTemplate
Extracts parameters with default values from a CloudFormation tempalte to JSON file that can be used to deploy the same template with default values using CodePipeline

# Usage
1. Specify the template file (yml). Relative paths are allowed. Some limitations exist.
1. Specify the output configuration file (json). Relative paths are allowed. Some limitations exist.
1. Optional parameters overrideParams can be used to overwrite specific parameter values with customs (non-default values). Must be a valid JSON string.

## Example
```bash
GetParametersFromTemplate.py 'CloudFormation/template.yml' 'Configuration/template-configuration.json' '--overrideParams' '{\"Key1\": \"Value1\", \"Key2\": \"Value2\", \"Key3\": \"Key3\", \"Key4\": \"Value4\", \"Key5\": \"Value5\"}'
```
