import time

from smartz.api.constructor_engine import ConstructorInstance


class Constructor(ConstructorInstance):

    def get_version(self):
        return {
            "result": "success",
            "version": 1
        }

    def get_params(self):
        json_schema = {
            "type": "object",
            "required": [
                "string", "integer", "enum"
            ],
            "additionalProperties": False,

            "properties": {
                "string": {
                    "title": "String field",
                    "description": "Length from 3 to 30 characters wit pattern [0-9a-z]. Required",
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 30,
                    "pattern": "^[a-z0-9]+$"
                },

                "integer": {
                    "title": "Integer field",
                    "description": "from 2 to 100 inclusive. Required",
                    "minimum": 2,
                    "maximum": 100,
                    "type": "integer"
                },

                "boolean_checkbox": {
                    "title": "Boolean field with checkbox",
                    "type": "boolean"
                },

                "enum": {
                    "title": "Radiobox (several string variants)",
                    "description": "Default - variant 2",
                    "type": "string",
                    "default": 'Without errors',
                    "enum": [
                        'Global error', 'Without errors', 'Fields error'
                    ]
                },

                "number": {
                    "title": "Float field",
                    "description": "from 2 to 100 inclusive",
                    "minimum": 2,
                    "maximum": 100,
                    "type": "number"
                },


                "ethCountPositive": {
                    "title": "Positive ether count",
                    "description": "Float like field with without exp notation. Greater than zero",
                    "$ref": "#/definitions/ethCountPositive"
                },

                "ethCount": {
                    "title": "Ether count",
                    "description": "Float like field with without exp notation. Greater or equal zero",
                    "$ref": "#/definitions/ethCountPositive"
                },


                "unxtimeWidget": {
                    "title": "Unixtime with widget",
                    "description": "Unixtime will be sent",
                    "$ref": "#/definitions/unixTime"
                },

                "address": {
                    "title": "Address",
                    "description": "See for more definitions https://github.com/smartzplatform/SDK/blob/master/json-schema/ethereum-sc.json",
                    "$ref": "#/definitions/address"
                },

                "fileHash": {
                    "title": "File hash",
                    "description": "Just upload file, hash (keccak256) of it will be sent",
                    "$ref": "#/definitions/hash"
                },

                "stringHash": {
                    "title": "String hash",
                    "description": "Just type text, hash (keccak256) of it will be sent",
                    "$ref": "#/definitions/hash"
                },

                "addressArray": {
                    "title": "Address array",
                    "description": "Address array with minimum 1 element",
                    "minItems": 1,
                    "$ref": "#/definitions/addressArray"
                },


            }
        }

        ui_schema = {
            "enum": {
                "ui:widget": "radio",
            },
            "unxtimeWidget": {
                "ui:widget": "unixTime",
            },
            "fileHash": {
                "ui:widget": "fileHash",
            },
            "stringHash": {
                "ui:widget": "stringHash",
            },
        }

        return {
            "result": "success",
            "schema": json_schema,
            "ui_schema": ui_schema
        }

    def construct(self, fields_vals):

        if fields_vals['enum'] == 'Global error':
            return {
                "result": "error",
                "error_descr": 'Global error'
            }

        if fields_vals['enum'] == 'Fields error':
            return {
                "result": "error",
                "errors": {
                    'string': 'some error',
                    'enum': ['some error 1', 'some error 2']
                }
            }


        return {
            "result": "success",
            'source': self._TEMPLATE,
            'contract_name': "SmartzFeatures"
        }

    def post_construct(self, fields, abi_array):

        function_titles = {

            'publicVar': {
                'title': 'Public var',
                'description': 'View function for public var',
                'sorting_order': 5
            },

            'cubeIt': {
                'title': 'Cube it',
                'description': 'Ask fuction for cube some integer',
                'sorting_order': 10,
                'inputs': [
                    {'title': 'some int', 'description': 'to be cubed'}
                ]
            },

            'widgetFeatures': {
                'title': 'Widget features',
                'description': 'String hash, file hash widgets for input params, titles for outputs',
                'sorting_order': 20,
                'inputs': [
                    {
                        'title': 'string hash',
                        'description': 'Hash of string will be sent as param to smart contract function',
                        'ui:widget': 'stringHash'
                    },
                    {
                        'title': 'file hash',
                        'description': 'Hash of file will be sent as param to smart contract function',
                        'ui:widget': 'fileHash'
                    },
                    {
                        'title': 'unix time',
                        'description': 'unix timestamp will be sent as param to smart contract function',
                        'ui:widget': 'unixTime'
                    },
                ],
                'outputs': [
                    {'title': 'string hash'},
                    {'title': 'file hash'},
                    {'title': 'unix timestamp + 3'}
                ]
            },

            'ethCount': {
                'title': 'some eth count',
                'description': 'In variable in smart contract it stored in wei',
                'ui:widget': 'ethCount',
                'sorting_order': 50
            },


            'someState': {
                'title': 'Some state',
                'description': 'Represents solidity enum as string',
                'ui:widget': 'enum',
                'ui:widget_options': {
                    'enum': ['READY', 'STEADY', 'GO']
                },
                'sorting_order': 80
            },

            'someDate': {
                'title': 'Some date',
                'description': 'With custom format (see https://www.npmjs.com/package/dateformat)',
                'ui:widget': 'unixTime',
                'ui:widget_options': {
                    'format': "yyyy.mm.dd HH:MM:ss (o)"
                },
                'sorting_order': 85
            },

            'setState': {
                'title': 'Set some state',
                'description': 'Write function',
                'inputs': [
                    {'title': 'Int representation of state', 'description': '0 - READY, 1 - STEADY, 2 - GO'}
                ],
                'sorting_order': 90
            },

            'setDate': {
                'title': 'Set some date',
                'inputs': [
                    {'title': 'Date time selector', 'description': 'unixtime will be sent', 'ui:widget': 'unixTime'}
                ],
                'sorting_order': 100
            },
        }

        return {
            "result": "success",
            'function_specs': function_titles,
            'dashboard_functions': ['publicVar', 'someState']
        }


    # language=Solidity
    _TEMPLATE = """
/**
 * Copyright (C) 2018 Smartz, LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND (express or implied).
 */

pragma solidity ^0.4.20;


/**
 * @title Booking
 * @author Vladimir Khramov <vladimir.khramov@smartz.io>
 */
contract SmartzFeatures {

    function SmartzFeatures() public payable {
       
        %payment_code%
    }

   
    
    string public publicVar = 'Some text';
    
    
    uint private cube = 3;
    function cubeIt(uint256 _var) public view returns (uint256) {
        return _var**cube;
    }
    
    function widgetFeatures(bytes32 _hash1, bytes32 _hash2, uint256 _timestamp) 
        public view returns (bytes32, bytes32, uint256) 
    {
        return (_hash1, _hash2, _timestamp + cube);
    }
    
    uint256 public ethCount = 1.2 ether;
    
    
    enum State {READY, STEADY, GO}
    State public someState = State.STEADY;
    
    function setState(State _state) public {
        someState = _state;
    }
    
    uint256 public someDate = now;
    
    function setDate(uint256 _date) public {
        someDate = _date;
    }

}

    """
