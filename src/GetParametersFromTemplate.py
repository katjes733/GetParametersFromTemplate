# MIT License

# Copyright (c) 2021 Martin Macecek

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse, sys, yaml, io, json, os, re, rstr
from pathlib import Path

def validate_json_string(arg_value):
    try:
        print(arg_value)
        json.loads(arg_value)
    except Exception as error: 
        raise argparse.ArgumentTypeError(f"{arg_value} is no valid JSON string.")
    return arg_value 

parser = argparse.ArgumentParser()
parser.add_argument('template', help='The file name of the CloudFormation template')
parser.add_argument('configFile', help='The (output) file name of the generated JSON configuration')
parser.add_argument('--overrideParams', type=validate_json_string, help='The key/pair values to override as JSON')
args = parser.parse_args()

template = args.template
template_config = args.configFile

def get_parameters_from_template():
    dict = None
    output = io.StringIO()
    with open(template, 'r') as stream:
        for line in stream:
            if 'Metadata:' in line or 'Resources:' in line:            
                break
            else:            
                output.write(line)    
    output.seek(0)
    dict = yaml.full_load(output)
    return dict['Parameters']

def generate_default_value(parameter): 
    defaultValue = '' 
    if parameter['Type'] == 'String':
        if 'AllowedPattern' in parameter and not re.match(parameter['AllowedPattern'], defaultValue):
            defaultValue = rstr.xeger(parameter['AllowedPattern'])
        if 'MinLength' in parameter:
            defaultValue = rstr.xeger(f"\w{{{parameter['MinLength']}}}")
    elif parameter['Type'] == 'Number':
        defaultValue = '0'
        if 'MinValue' in parameter:
            defaultValue = f"{parameter['MinValue']}"
    return defaultValue

def prepare_configuration(params):
    config = {}
    for pName in params.keys():
        if 'Default' in params[pName]:
            value = params[pName]['Default']
            config[pName] = f"{str(value).lower() if type(value) is bool else value}"
        elif 'AllowedValues' in params[pName] and params[pName]['AllowedValues']:
            config[pName] = params[pName]['AllowedValues'][0]
        else:
            config[pName] = generate_default_value(params[pName])
    return config

def override_parameters(config):
    if args.overrideParams:
        overrides = json.loads(args.overrideParams)
        for key in overrides.keys(): 
            if key in config:
                config[key] = overrides[key]
    return config

def create_parameters_json_file(config):
    result = {'Parameters': config}
    json_content = json.dumps(result, indent = 4)
    Path(Path(template_config).parent).mkdir(parents=True, exist_ok=True)
    configFile = open(template_config, 'w')
    print(json_content, file=configFile)
    configFile.close()

def process():
    print(f"Template: {template}")
    params = get_parameters_from_template()
    prepared_config = prepare_configuration(params)
    completed_config = override_parameters(prepared_config)
    create_parameters_json_file(completed_config)

try:
    print("Starting function") 
    process()
    print("Finished function")
except Exception as error:
    print(f"Error {error}")
    raise