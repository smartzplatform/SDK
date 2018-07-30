from typing import Dict

from smartz.api.constructor_engine import ConstructorInstance


def is_true(arr, key):
    return key in arr and bool(arr[key])


class Constructor(ConstructorInstance):

    _SWAP_TYPE_ETHER  = 'Ether'
    _SWAP_TYPE_TOKENS = 'ERC20 tokens'
    
    def __init__(self):
        self._TEMPLATES: Dict[str, str] = {
            self._SWAP_TYPE_ETHER:  self._TEMPLATE_TOKENS_FOR_ETHER,
            self._SWAP_TYPE_TOKENS: self._TEMPLATE_TOKENS_FOR_TOKENS
        }
        
        self._CHECK_TRANSFER1: Dict[str, str] = {
            self._SWAP_TYPE_ETHER:  self._TEMPLATE_TOKENS_FOR_ETHER_CHECK_TRANSFER1,
            self._SWAP_TYPE_TOKENS: self._TEMPLATE_TOKENS_FOR_TOKENS_CHECK_TRANSFER1
        }
        
        self._CHECK_TRANSFER2: Dict[str, str] = {
            self._SWAP_TYPE_ETHER:  self._TEMPLATE_TOKENS_FOR_ETHER_CHECK_TRANSFER2,
            self._SWAP_TYPE_TOKENS: self._TEMPLATE_TOKENS_FOR_TOKENS_CHECK_TRANSFER2
        }

    def get_version(self):
        return {
            "result": "success",
            "version": 1
        }

    def get_params(self):
        json_schema = {
            "type": "object",
            "required": ["participant1", "participant2"],
            "additionalProperties": False,

            "properties": {
                "participant1": {
                    "type": "object",
                    "title": "Participant #1",

                    "required": ["token", "count"],

                    "properties": {
                        "use_my_address": {
                            "type": "boolean",
                            "title": "Use my address",
                            "description": "Deployer's address would be got as participant #1 address",
                            "default": True
                        },

                        "token": {
                            "title": "Token address",
                            "description": "Address of ERC20 token smart contract, which participant #1 will swap",
                            "$ref": "#/definitions/address"
                        },

                        "count": {
                            "title": "Tokens count",
                            "description": "Tokens count, which participant #1 will swap for participant #2 tokens/ether. Token decimals must be <= 18",
                            "type": "string",
                            "pattern": "^([1-9][0-9]{0,54}|[0-9]{1,55}\.[0-9]{0,17}[1-9])$"
                        }
                    },
                    "dependencies": {
                        "use_my_address": {
                            "oneOf": [
                                {
                                    "properties": {
                                        "use_my_address": {
                                            "enum": [
                                                True
                                            ]
                                        },
                                    },
                                },
                                {
                                    "properties": {
                                        "use_my_address": {
                                            "enum": [
                                                False
                                            ]
                                        },
                                        "address": {
                                            "title": "Address",
                                            "description": "Address where tokens/ether from participant #2 will be sent",
                                            "$ref": "#/definitions/address"
                                        },
                                    },
                                    "required": [
                                        "address"
                                    ]
                                }
                            ]
                        }
                    }
                },

                "participant2": {
                    "type": "object",
                    "title": "Participant #2",

                    "required": ["swap_type"],

                    "properties": {
                        "swap_type": {
                            "title": "Swap type",
                            "description": "Swap tokens of participant #1 for participant's #2:",

                            "type": "string",
                            "enum": [
                                self._SWAP_TYPE_ETHER,
                                self._SWAP_TYPE_TOKENS
                            ],
                            "default": self._SWAP_TYPE_ETHER
                        },
                        "use_my_address": {
                            "type": "boolean",
                            "title": "Use my address",
                            "description": "Deployer's address would be got as participant #1 address",
                            "default": False
                        },
                    },
                    "dependencies": {
                        "use_my_address": {
                            "oneOf": [
                                {
                                    "properties": {
                                        "use_my_address": {
                                            "enum": [
                                                True
                                            ]
                                        },
                                    },
                                },
                                {
                                    "properties": {
                                        "use_my_address": {
                                            "enum": [
                                                False
                                            ],
                                        },
                                        "address": {
                                            "title": "Address",
                                            "description": "Address where tokens/ether from participant #1 will be sent",
                                            "$ref": "#/definitions/address"
                                        },
                                    },
                                    "required": [
                                        "address"
                                    ]
                                }
                            ]
                        },
                        "swap_type": {
                            "oneOf": [
                                {
                                    "properties": {
                                        "swap_type": {
                                            "enum": [
                                                self._SWAP_TYPE_ETHER
                                            ]
                                        },
                                        "count": {
                                            "title": "Ether count",
                                            "description": "Ether count, which participant #2 will swap for participant #2 tokens",
                                            "type": "string",
                                            "pattern": "^([1-9][0-9]{0,54}|[0-9]{1,55}\.[0-9]{0,17}[1-9])$"
                                        }
                                    },
                                    "required": [
                                        "count"
                                    ]
                                },
                                {
                                    "properties": {
                                        "swap_type": {
                                            "enum": [
                                                self._SWAP_TYPE_TOKENS
                                            ]
                                        },

                                        "token": {
                                            "title": "Token address",
                                            "description": "Address of ERC20 token smart contract, which participant #2 will swap",
                                            "$ref": "#/definitions/address"
                                        },

                                        "count": {
                                            "title": "Tokens count",
                                            "description": "Tokens count, which participant #2 will swap for participant #1 tokens. . Token decimals must be <= 18",
                                            "type": "string",
                                            "pattern": "^([1-9][0-9]{0,54}|[0-9]{1,55}\.[0-9]{0,17}[1-9])$"
                                        }
                                    },
                                    "required": [
                                        "token", "count"
                                    ]
                                }
                            ]
                        }
                    }
                },

                "check_transfers": {
                    "type": "boolean",
                    "title": "Verify token transfers",
                    "description": "Verify that token balances of participants after swap are greater for the amount of transfer (or more). If not, the transaction will be canceled.",
                    "default": True
                },

            }
        }

        ui_schema = {
            "participant1": {
                "ui:order": ["*", "token", "count"],
            },
            "participant2": {
                "swap_type": {
                    "ui:widget": "radio",
                }
            }
        }

        return {
            "result": "success",
            "schema": json_schema,
            "ui_schema": ui_schema
        }

    def construct(self, fields):
        
        swap_type = fields['participant2']['swap_type']
        part1 = fields['participant1']
        part2 = fields['participant2']

        errors = self._check_errors(part1, part2, swap_type)
        if errors:
            return {
                "result": "error",
                "errors": errors
            }

        source = self._TEMPLATES[swap_type]

        source = self._fill_check_transfers_dependant_vars(fields, source, swap_type)
        source = self._fill_main_vars(part1, part2, source)
        source = self._fill_swap_type_dependant_vars(part2, source, swap_type)

        return {
            "result": "success",
            'source': source,
            'contract_name': "Swap"
        }

    def post_construct(self, fields, abi_array):

        if fields['participant2']['swap_type'] == self._SWAP_TYPE_ETHER:
            part2_type = 'ether'
        else:
            part2_type = 'tokens'

        function_titles = {
            'isFinished': {
                'title': 'Is finished?',
                'description': 'is swap finished',
                'sorting_order': 10
            },

            'participant1': {
                'title': 'Participant #1',
                'description': 'Address of participant #1',
                'sorting_order': 20

            },

            "participant1Token": {
                "title": "Token address of participant #1",
                "description": "Address of ERC20 token smart contract, which participant #1 will swap",
                'sorting_order': 30
            },

            "participant1TokensCount": {
                "title": "Tokens count of participant #1 (in token wei)",
                "description": "Tokens count, which participant #1 will swap for participant #2 tokens/ether (in token wei)",
                'sorting_order': 40
            },

            "participant1SentTokensCount": {
                "title": "Tokens count sent by participant #1 (in token wei)",
                "description": "Tokens count, which participant #1 has already sent (in token wei)",
                'sorting_order': 50
            },

            'participant2': {
                'title': 'Participant #2',
                'description': 'Address of participant #2',
                'sorting_order': 60
            },

            'swap': {
                'title': 'Swap',
                'description': 'Swap tokens of participant #1 to {} of participant #2'.format(part2_type),
                'sorting_order': 100
            },

            'refund': {
                'title': 'Refund',
                'description': 'Refund tokens/ether to participants',
                'sorting_order': 110
            },
        }

        if fields['participant2']['swap_type'] == self._SWAP_TYPE_ETHER:
            function_titles["participant2EtherCount"] = {
                "title": "Ether count of participant #2 (in wei)",
                "description": "Ether count, which participant #1 will swap for participant #2 tokens (in wei)",
                'sorting_order': 70
            }
            function_titles["participant2SentEtherCount"] = {
                "title": "Ether count sent by participant #2 (in wei)",
                "description": "Ether count, which participant #2 has already sent (in wei)",
                'sorting_order': 80
            }
        else:
            function_titles["participant2Token"] = {
                "title": "Token address of participant #2",
                "description": "Address of ERC20 token smart contract, which participant #2 will swap",
                'sorting_order': 70
            }
            function_titles["participant2TokensCount"] = {
                "title": "Tokens count of participant #2 (in token wei)",
                "description": "Tokens count, which participant #2 will swap for participant #1 tokens (in token wei)",
                'sorting_order': 80
            }
            function_titles["participant2SentTokensCount"] = {
                "title": "Tokens count sent by participant #2 (in token wei)",
                "description": "Tokens count, which participant #2 has already sent (in token wei)",
                'sorting_order': 90
            }

        return {
            "result": "success",
            'function_specs': function_titles,
            'dashboard_functions': ['isFinished', 'participant1', 'participant2']
        }

    def _check_errors(self, part1, part2, swap_type):
        """ Check additional errors"""
        errors = {}

        if "address" in part1 and "address" in part2 \
                and part1['address'] == part2['address']:
            errors['participant1'] = {
                'address': "Participants addresses must be different"
            }

        if is_true(part1, "use_my_address") and is_true(part2, "use_my_address"):
            errors['participant1'] = {
                'use_my_address': "Participants addresses must be different"
            }

        if swap_type == self._SWAP_TYPE_TOKENS and part1['token'] == part2['token']:
            if 'participant1' not in errors:
                errors['participant1'] = {}
            errors['participant1']['token'] = "Tokens addresses must be different"

        return errors

    def _fill_swap_type_dependant_vars(self, part2, source, swap_type):
        if swap_type == self._SWAP_TYPE_ETHER:
            source = source \
                .replace('%_participant2EtherCount%', str(part2['count']))
        else:
            source = source \
                .replace('%_participant2TokenAddress%', part2['token']) \
                .replace('%_participant2TokensCount%', str(part2['count']))
        return source

    def _fill_main_vars(self, part1, part2, source):

        part1_address = 'msg.sender' if is_true(part1, "use_my_address") else part1['address']
        part2_address = 'msg.sender' if is_true(part2, "use_my_address") else part2['address']

        source = source \
            .replace('%erc20_basic%', self._TEMPLATE_ERC20) \
            .replace('%_participant1%', part1_address) \
            .replace('%_participant2%', part2_address) \
            .replace('%_participant1TokenAddress%', part1['token']) \
            .replace('%_participant1TokensCount%', str(part1['count']))
        return source

    def _fill_check_transfers_dependant_vars(self, fields, source, swap_type):
        """ Fill check transfers templates"""
        if 'check_transfers' in fields and fields['check_transfers']:
            source = source \
                .replace('%check_transfers1%', self._CHECK_TRANSFER1[swap_type]) \
                .replace('%check_transfers2%', self._CHECK_TRANSFER2[swap_type])
        else:
            source = source \
                .replace('%check_transfers1%', '') \
                .replace('%check_transfers2%', '')

        return source

    # language=Solidity
    _TEMPLATE_ERC20 = """
/**
 * @title ERC20Basic
 * @dev Simpler version of ERC20 interface
 * @dev see https://github.com/ethereum/EIPs/issues/179
 */
contract ERC20Basic {
  uint8 public decimals;

  uint256 public totalSupply;
  function balanceOf(address who) public view returns (uint256);
  function transfer(address to, uint256 value) public returns (bool);
  event Transfer(address indexed from, address indexed to, uint256 value);
}
    """

    # language=Solidity
    _TEMPLATE_TOKENS_FOR_ETHER = """
pragma solidity ^0.4.18;


%erc20_basic%

/**
 * Copyright (C) 2018  Smartz, LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND (express or implied).
 */
 
/**
 * @title SwapTokenForEther
 * Swap tokens of participant1 for ether of participant2
 *
 * @author Vladimir Khramov <vladimir.khramov@smartz.io>
 */
contract Swap {

    address public participant1;
    address public participant2;

    ERC20Basic public participant1Token;
    uint256 public participant1TokensCount;

    uint256 public participant2EtherCount;

    bool public isFinished = false;


    function Swap() public payable {

        participant1 = %_participant1%;
        participant2 = %_participant2%;

        participant1Token = ERC20Basic(%_participant1TokenAddress%);
        require(participant1Token.decimals() <= 18);
        
        participant1TokensCount = %_participant1TokensCount% ether / 10**(18-uint256(participant1Token.decimals()));

        participant2EtherCount = %_participant2EtherCount% ether;
        
        assert(participant1 != participant2);
        assert(participant1Token != address(0));
        assert(participant1TokensCount > 0);
        assert(participant2EtherCount > 0);
        
        %payment_code%
    }

    /**
     * Ether accepted
     */
    function () external payable {
        require(!isFinished);
        require(msg.sender == participant2);

        if (msg.value > participant2EtherCount) {
            msg.sender.transfer(msg.value - participant2EtherCount);
        }
    }

    /**
     * Swap tokens for ether
     */
    function swap() external {
        require(!isFinished);

        require(this.balance >= participant2EtherCount);

        uint256 tokensBalance = participant1Token.balanceOf(this);
        require(tokensBalance >= participant1TokensCount);

        isFinished = true;
        
        %check_transfers1%

        require(participant1Token.transfer(participant2, participant1TokensCount));
        if (tokensBalance > participant1TokensCount) {
            require(
                participant1Token.transfer(participant1, tokensBalance - participant1TokensCount)
            );
        }

        participant1.transfer(this.balance);
        
        %check_transfers2%
    }

    /**
     * Refund tokens or ether by participants
     */
    function refund() external {
        if (msg.sender == participant1) {
            uint256 tokensBalance = participant1Token.balanceOf(this);
            require(tokensBalance>0);

            participant1Token.transfer(participant1, tokensBalance);
        } else if (msg.sender == participant2) {
            require(this.balance > 0);
            participant2.transfer(this.balance);
        } else {
            revert();
        }
    }
    

    /**
     * Tokens count sent by participant #1
     */
    function participant1SentTokensCount() public view returns (uint256) {
        return participant1Token.balanceOf(this);
    }

    /**
     * Ether count sent by participant #2
     */
    function participant2SentEtherCount() public view returns (uint256) {
        return this.balance;
    }
}
    """


    # language=Solidity
    _TEMPLATE_TOKENS_FOR_TOKENS = """
pragma solidity ^0.4.18;

%erc20_basic%

/**
 * Copyright (C) 2018  Smartz, LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND (express or implied).
 */
 
/**
 * @title SwapTokenForToken
 * Swap tokens of participant1 for tokens of participant2
 *
 * @author Vladimir Khramov <vladimir.khramov@smartz.io>
 */
contract Swap {

    address public participant1;
    address public participant2;

    ERC20Basic public participant1Token;
    uint256 public participant1TokensCount;

    ERC20Basic public participant2Token;
    uint256 public participant2TokensCount;

    bool public isFinished = false;

    /**
     * Constructor
     */
    function Swap() public payable {
        participant1 = %_participant1%;
        participant2 = %_participant2%;

        participant1Token = ERC20Basic(%_participant1TokenAddress%);
        require(participant1Token.decimals() <= 18);
        participant1TokensCount = %_participant1TokensCount% ether / 10**(18-uint256(participant1Token.decimals()));

        participant2Token = ERC20Basic(%_participant2TokenAddress%);
        require(participant2Token.decimals() <= 18);
        participant2TokensCount = %_participant2TokensCount% ether / 10**(18-uint256(participant2Token.decimals()));
        
        assert(participant1 != participant2);
        assert(participant1Token != participant2Token);
        assert(participant1Token != address(0));
        assert(participant2Token != address(0));
        assert(participant1TokensCount > 0);
        assert(participant2TokensCount > 0);
        
        %payment_code%
    }

    /**
     * No direct payments
     */
    function() external {
        revert();
    }

    /**
     * Swap tokens for tokens
     */
    function swap() external {
        require(!isFinished);

        uint256 tokens1Balance = participant1Token.balanceOf(this);
        require(tokens1Balance >= participant1TokensCount);

        uint256 tokens2Balance = participant2Token.balanceOf(this);
        require(tokens2Balance >= participant2TokensCount);

        isFinished = true;
        
        %check_transfers1%

        require(participant1Token.transfer(participant2, participant1TokensCount));
        if (tokens1Balance > participant1TokensCount) {
            require(
                participant1Token.transfer(participant1, tokens1Balance - participant1TokensCount)
            );
        }

        require(participant2Token.transfer(participant1, participant2TokensCount));
        if (tokens2Balance > participant2TokensCount) {
            require(
                participant2Token.transfer(participant2, tokens2Balance - participant2TokensCount)
            );
        }
        
        %check_transfers2%
    }

    /**
     * Refund tokens by participants
     */
    function refund() external {
        if (msg.sender == participant1) {
            uint256 tokens1Balance = participant1Token.balanceOf(this);
            require(tokens1Balance > 0);

            participant1Token.transfer(participant1, tokens1Balance);
        } else if (msg.sender == participant2) {
            uint256 tokens2Balance = participant2Token.balanceOf(this);
            require(tokens2Balance > 0);

            participant2Token.transfer(participant2, tokens2Balance);
        } else {
            revert();
        }
    }
    
    /**
     * Tokens count sent by participant #1
     */
    function participant1SentTokensCount() public view returns (uint256) {
        return participant1Token.balanceOf(this);
    }

    /**
     * Tokens count sent by participant #2
     */
    function participant2SentTokensCount() public view returns (uint256) {
        return participant2Token.balanceOf(this);
    }
}
    """

    # language=Solidity
    _TEMPLATE_TOKENS_FOR_ETHER_CHECK_TRANSFER1 = """
        //check transfer
        uint token1Participant2InitialBalance = participant1Token.balanceOf(participant2);
    """

    # language=Solidity
    _TEMPLATE_TOKENS_FOR_ETHER_CHECK_TRANSFER2 = """
        //check transfer
        assert(participant1Token.balanceOf(participant2) >= token1Participant2InitialBalance+participant1TokensCount);
    """

    # language=Solidity
    _TEMPLATE_TOKENS_FOR_TOKENS_CHECK_TRANSFER1 = """
        //check transfer
        uint token1Participant2InitialBalance = participant1Token.balanceOf(participant2);
        uint token2Participant1InitialBalance = participant2Token.balanceOf(participant1);
    """

    # language=Solidity
    _TEMPLATE_TOKENS_FOR_TOKENS_CHECK_TRANSFER2 = """
        //check transfer
        assert(participant1Token.balanceOf(participant2) >= token1Participant2InitialBalance+participant1TokensCount);
        assert(participant2Token.balanceOf(participant1) >= token2Participant1InitialBalance+participant2TokensCount);
    """
