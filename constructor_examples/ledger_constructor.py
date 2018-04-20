import re
import time

from smartz.api.constructor_engine import ConstructorInstance

class Field():
    def __init__(self, name, type, ui_widget=None):
        self.name = name
        self.type = type
        self.ui_widget = ui_widget

    def default_val(self):
        return "''" if self.type == 'string' else "0"


    def checkbox_name(self):
        """checkbox field name"""
        return 'use_{}_field'.format(self.name)

    def block_name(self):
        """name of block for this field"""
        return '{}_field'.format(self.name)

    def descr_field_name(self):
        """field description field name"""
        return '{}_field_descr'.format(self.name)

    def mapping_name(self, fields_vals):
        """name of mapping for search by this field"""
        return '{}_mapping'.format(self.field_name(fields_vals))

    def field_descr(self, fields_vals):
        return fields_vals[ self.block_name()][ self.descr_field_name()]

    def field_name(self, fields_vals):
        """name of solidity variable (human readable)"""
        descr = self.field_descr(fields_vals)

        lower_first = lambda s: s[:1].lower() + s[1:] if s else ''

        return re.sub('[^a-zA-Z]', '', lower_first(descr.title()))

    def mapping_code(self, fields_vals):
        return "    mapping (bytes32 => uint256) {};".format(self.mapping_name(fields_vals))

    def find_function_name(self, fields_vals):
        upper_first = lambda s: s[:1].upper() + s[1:] if s else ''
        return 'findBy{0}'.format(upper_first(self.field_name(fields_vals)))

    def find_id_function_name(self, fields_vals):
        upper_first = lambda s: s[:1].upper() + s[1:] if s else ''

        return 'findIdBy{0}'.format(upper_first(self.field_name(fields_vals)))

    def mapping_check(self, fields_vals):
        return "        require(0=={}(_{}));".format(
            self.find_id_function_name(fields_vals),
            self.field_name(fields_vals),
        )

    def find_function(self, fields_vals, contract_add_record_params, contract_add_record__record_vars):
        return """
    function {find_name}({type} _{field_name}) public view returns (uint256 id, {return_params}) {{
        Record record = records[ {find_id_name}(_{field_name}) ];
        return (
            {find_id_name}(_{field_name}),
            {vars}
        );
    }}
    
    function {find_id_name}({type} {field_name}) internal view returns (uint256) {{
        return {mapping_name}[{hash_fn}({field_name})];
    }}""".format(
            find_name=self.find_function_name(fields_vals),
            find_id_name=self.find_id_function_name(fields_vals),
            type=self.type,
            field_name=self.field_name(fields_vals),
            mapping_name=self.mapping_name(fields_vals),
            hash_fn='' if self.type == 'bytes32' else 'keccak256',
            return_params=', '.join(contract_add_record_params),
            vars=', '.join(['record.{}'.format(x) for x in contract_add_record__record_vars])
        )

    def add_to_mapping(self, fields_vals):
        return """        {0}[{1}(_{2})] = records.length-1;""".format(
            self.mapping_name(fields_vals),
            '' if self.type == 'bytes32' else 'keccak256',
            self.field_name(fields_vals)
        )


class Constructor(ConstructorInstance):

    FIELD_TYPES = {
        'text': Field(
            name='text',
            type='string'
        ),
        'text_hash': Field(
            name='text_hash',
            type='bytes32',
            ui_widget='stringHash'
        ),
        'url': Field(
            name='url',
            type='string'
        ),
        'file_hash': Field(
            name='file_hash',
            type='bytes32',
            ui_widget='fileHash'
        ),
    }


    def get_version(self):
        return {
            "result": "success",
            "version": 1
        }

    def get_params(self):
        json_schema = {
            "type": "object",
            "required": [
                "description", "name", "record_name"
            ],

            "properties": {
                "name": {
                    "title": "Ledger name",
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 200,
                    "pattern": "^[a-zA-Z0-9,\.\?\$\:\& ]+$"
                },
                "description": {
                    "title": "Ledger description",
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 1000,
                    "pattern": "^[a-zA-Z0-9,\.\?\$\:\& ]+$"
                },
                "record_name": {
                    "title": "Record name",
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 1000,
                    "pattern": "^[a-zA-Z0-9 ]+$"
                },

                "text_field": {
                    "title": "Text field",
                    "type": "object",
                    "properties": {
                        "use_text_field": {
                            "type": "boolean",
                            "title": "Use text field",
                            "description": "Todo",
                            "default": True
                        },
                    },
                    "dependencies": {
                        "use_text_field": {
                            "oneOf": [
                                {
                                    "properties": {
                                        "use_text_field": {
                                            "enum": [
                                                False
                                            ]
                                        },
                                    },
                                },
                                {
                                    "properties": {
                                        "use_text_field": {
                                            "enum": [
                                                True
                                            ]
                                        },
                                        "text_field_descr": {
                                            "title": "Text field description",
                                            "type": "string",
                                            "minLength": 3,
                                            "maxLength": 30,
                                            "pattern": "^[a-zA-Z0-9,\.\?\$\:\& ]+$"
                                        },
                                    },
                                    "required": [
                                        "text_field_descr"
                                    ]
                                }
                            ]
                        },

                    }
                },
                "text_hash_field": {
                    "title": "Text hash field",
                    "type": "object",
                    "properties": {
                        "use_text_hash_field": {
                            "type": "boolean",
                            "title": "Use text hash field",
                            "description": "Todo",
                            "default": False
                        },
                    },
                    "dependencies": {
                        "use_text_hash_field": {
                            "oneOf": [
                                {
                                    "properties": {
                                        "use_text_hash_field": {
                                            "enum": [
                                                False
                                            ]
                                        },
                                    },
                                },
                                {
                                    "properties": {
                                        "use_text_hash_field": {
                                            "enum": [
                                                True
                                            ]
                                        },
                                        "text_hash_field_descr": {
                                            "title": "Text hash field description",
                                            "type": "string",
                                            "minLength": 3,
                                            "maxLength": 30,
                                            "pattern": "^[a-zA-Z0-9,\.\?\$\:\& ]+$"
                                        },
                                    },
                                    "required": [
                                        "text_hash_field_descr"
                                    ]
                                }
                            ]
                        },

                    }
                },
                "url_field": {
                    "title": "Url field",
                    "type": "object",
                    "properties": {
                        "use_url_field": {
                            "type": "boolean",
                            "title": "Use url field",
                            "description": "Todo",
                            "default": False
                        },
                    },
                    "dependencies": {
                        "use_url_field": {
                            "oneOf": [
                                {
                                    "properties": {
                                        "use_url_field": {
                                            "enum": [
                                                False
                                            ]
                                        },
                                    },
                                },
                                {
                                    "properties": {
                                        "use_url_field": {
                                            "enum": [
                                                True
                                            ]
                                        },
                                        "url_field_descr": {
                                            "title": "Url field description",
                                            "type": "string",
                                            "minLength": 3,
                                            "maxLength": 30,
                                            "pattern": "^[a-zA-Z0-9,\.\?\$\:\& ]+$"
                                        },
                                    },
                                    "required": [
                                        "url_field_descr"
                                    ]
                                }
                            ]
                        },

                    }
                },
                "file_hash_field": {
                    "title": "File hash field",
                    "type": "object",
                    "properties": {
                        "use_file_hash_field": {
                            "type": "boolean",
                            "title": "Use file hash field",
                            "description": "Todo",
                            "default": False
                        },
                    },
                    "dependencies": {
                        "use_file_hash_field": {
                            "oneOf": [
                                {
                                    "properties": {
                                        "use_file_hash_field": {
                                            "enum": [
                                                False
                                            ]
                                        },
                                    },
                                },
                                {
                                    "properties": {
                                        "use_file_hash_field": {
                                            "enum": [
                                                True
                                            ]
                                        },
                                        "file_hash_field_descr": {
                                            "title": "File hash field description",
                                            "type": "string",
                                            "minLength": 3,
                                            "maxLength": 30,
                                            "pattern": "^[a-zA-Z0-9,\.\?\$\:\& ]+$"
                                        },
                                    },
                                    "required": [
                                        "file_hash_field_descr"
                                    ]
                                }
                            ]
                        },

                    }
                },
            },

        }

        ui_schema = {
            "text_field": {
                "ui:order": ["use_text_field", "*"],
            },
            "text_hash_field": {
                "ui:order": ["use_text_hash_field", "*"],
            },
            "url_field": {
                "ui:order": ["use_url_field", "*"],
            },
            "file_hash_field": {
                "ui:order": ["use_file_hash_field", "*"],
            }

        }

        return {
            "result": "success",
            "schema": json_schema,
            "ui_schema": ui_schema
        }

    def construct(self, fields_vals):

        errors = {}

        if self.is_false(fields_vals['text_field'], 'use_text_field') \
            and self.is_false(fields_vals['text_hash_field'], 'use_text_hash_field') \
            and self.is_false(fields_vals['url_field'], 'use_url_field') \
            and self.is_false(fields_vals['file_hash_field'], 'use_file_hash_field'):

            # todo waiting for front
            return {
                "result": "error",
                "error_descr": 'At least one field must be selected'
            }
            errors['text_field'] = {}
            errors['text_field']['use_text_field'] = 'At least one field must be selected'

        field_descr_exists = {}
        for field_instance in self.iterate_by_selected_fields(fields_vals):
            record_field_name = field_instance.field_name(fields_vals)
            if record_field_name in field_descr_exists:
                return {
                    "result": "error",
                    "error_descr": 'Fields descriptions must be unique'
                }
                errors[field_instance.block_name()] = {}
                errors[field_instance.block_name()][field_instance.descr_field_name()] = 'Fields descriptions must be unique'

            field_descr_exists[record_field_name] = True

            if 'id' == record_field_name:
                return {
                    "result": "error",
                    "error_descr": 'Fields descriptions must not be "id"'
                }
                errors[field_instance.block_name()] = {}
                errors[field_instance.block_name()][field_instance.descr_field_name()] = 'Fields descriptions must not be "id"'


        if errors:
            return {
                "result": "error",
                "errors": errors
            }


        contract_record_fields = []
        contract_record_fields__vars = []
        contract_mappings = []
        contract_check_record_exists = []
        contract_add_record_params = []
        contract_add_record__record_vars = []
        contract_add_record__record_empty = []
        contract_add_to_mappings = []

        contract_functions = []

        for field_instance in self.iterate_by_selected_fields(fields_vals):
            record_field_name = field_instance.field_name(fields_vals)

            contract_record_fields.append("{} {}".format(field_instance.type, record_field_name))
            contract_record_fields__vars.append(record_field_name)

            contract_add_record_params.append('{} _{}'.format(field_instance.type, record_field_name))
            contract_add_record__record_vars.append('_{}'.format(record_field_name))
            contract_add_record__record_empty.append(field_instance.default_val())

            contract_mappings.append(field_instance.mapping_code(fields_vals))
            contract_check_record_exists.append(field_instance.mapping_check(fields_vals))
            contract_add_to_mappings.append(field_instance.add_to_mapping(fields_vals))

        for field_instance in self.iterate_by_selected_fields(fields_vals):
            contract_functions.append(
                field_instance.find_function(fields_vals, contract_record_fields, contract_record_fields__vars)
            )


        source = self.__class__._TEMPLATE \
            .replace('%name%', fields_vals['name']) \
            .replace('%description%', fields_vals['description']) \
            .replace('%record_name%', fields_vals['record_name']) \
            .replace('%record_fields%', ';\n'.join(contract_record_fields) + ';') \
            .replace('%record_fields_comma_separated%', ', '.join(contract_record_fields)) \
            .replace('%add_record_params%', ','.join(contract_add_record_params)) \
            .replace('%add_record__record_vars%', ', '.join(contract_add_record__record_vars)) \
            .replace('%add_record__record_empty%', ','.join(contract_add_record__record_empty)) \
            .replace('%mappings%', "\n".join(contract_mappings)) \
            .replace('%check_record_exists%',  "\n".join(contract_check_record_exists)) \
            .replace('%add_to_mappings%',  "\n".join(contract_add_to_mappings))\
            .replace('%methods%',  "\n\n".join(contract_functions))


        return {
            "result": "success",
            'source': source,
            'contract_name': "Ledger"
        }

    def post_construct(self, fields_vals, abi_array):

        add_record_params = []
        record_outputs = []
        for field_instance in self.iterate_by_selected_fields(fields_vals):
            input_schema = {
                'title': field_instance.field_descr(fields_vals)
            }
            if field_instance.ui_widget:
                input_schema['ui:widget'] = field_instance.ui_widget

            add_record_params.append(input_schema)
            record_outputs.append({
                'title': field_instance.field_descr(fields_vals)
            })

        function_titles = {

            'name': {
                'title': 'Ledger name',
                'sorting_order': 10
            },

            'description': {
                'title': 'Ledger description',
                'sorting_order': 20
            },

            'recordName': {
                'title': 'Record type',
                'sorting_order': 30
            },

            'getRecordsCount': {
                'title': 'Records count',
                'sorting_order': 40
            },


            'addRecord': {
                'title': 'Add {} to ledger'.format(fields_vals['record_name']),
                "inputs": add_record_params,
                'sorting_order': 100
            },

            'records': {
                'title': 'Find record by id',
                'sorting_order': 110,
                "inputs": [
                    {"title": "{} ID".format(fields_vals['record_name'])}
                ],
                "outputs": record_outputs
            },

            'transferOwnership': {
                'title': 'Transfer ownership',
                'description': 'Transfer allowance to add new records to someone',
                "inputs": [
                    {"title": "Address of new owner"}
                ]
            }
        }


        for i, field_instance in enumerate(self.iterate_by_selected_fields(fields_vals)):
            fn_name = field_instance.find_function_name(fields_vals)

            input_schema = {"title": field_instance.field_descr(fields_vals)}
            if field_instance.ui_widget:
                input_schema['ui:widget'] = field_instance.ui_widget

            function_titles[fn_name] = {
                'title': 'Find {} by {}'.format(fields_vals['record_name'], field_instance.field_descr(fields_vals)),
                "sorting_order": 200 + i,
                "inputs": [
                    input_schema
                ],
                "outputs": [
                    {"title": "ID"}
                ] + record_outputs
            }



        return {
            "result": "success",
            'function_specs': function_titles,
            'dashboard_functions': ['name', 'description', 'recordName', 'getRecordsCount']
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
 * @title Ownable
 * @dev The Ownable contract has an owner address, and provides basic authorization control
 * functions, this simplifies the implementation of "user permissions".
 */
contract Ownable {
  address public owner;


  event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);


  /**
   * @dev The Ownable constructor sets the original `owner` of the contract to the sender
   * account.
   */
  function Ownable() public {
    owner = msg.sender;
  }


  /**
   * @dev Throws if called by any account other than the owner.
   */
  modifier onlyOwner() {
    require(msg.sender == owner);
    _;
  }


  /**
   * @dev Allows the current owner to transfer control of the contract to a newOwner.
   * @param newOwner The address to transfer ownership to.
   */
  function transferOwnership(address newOwner) public onlyOwner {
    require(newOwner != address(0));
    OwnershipTransferred(owner, newOwner);
    owner = newOwner;
  }

}


/**
 * @title Booking
 * @author Vladimir Khramov <vladimir.khramov@smartz.io>
 */
contract Ledger is Ownable {

    function Ledger() public payable {

        //empty element with id=0
        records.push(Record(%add_record__record_empty%));

        %payment_code%
    }
    
    /************************** STRUCT **********************/
    
    struct Record {
%record_fields%
    }
    
    /************************** EVENTS **********************/
    
    event RecordAdded(uint256 id, %record_fields_comma_separated%);
    
    /************************** CONST **********************/
    
    string public constant name = '%name%'; 
    string public constant description = '%description%'; 
    string public constant recordName = '%record_name%'; 

    /************************** PROPERTIES **********************/

    Record[] public records;
%mappings%

    /************************** EXTERNAL **********************/

    function addRecord(%add_record_params%) external onlyOwner returns (uint256) {
%check_record_exists%
    
    
        records.push(Record(%add_record__record_vars%));
        
%add_to_mappings%
        
        RecordAdded(records.length - 1, %add_record__record_vars%);
        
        return records.length - 1;
    }
    
    /************************** PUBLIC **********************/
    
    function getRecordsCount() public view returns(uint256) {
        return records.length - 1;
    }
    
    %methods%
}


    """

    def is_true(self, arr, key):
        return key in arr and bool(arr[key])

    def is_false(self, arr, key):
        return key not in arr or not bool(arr[key])


    def iterate_by_selected_fields(self, fields):
        for name, field_instance in self.FIELD_TYPES.items():
            if self.is_true(
                fields[ field_instance.block_name() ],
                field_instance.checkbox_name()
            ):
                yield field_instance