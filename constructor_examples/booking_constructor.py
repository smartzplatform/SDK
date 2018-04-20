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
                "description", "price", "cancellationFee", "rentDateStart", "rentDateEnd", "noCancelPeriod", "acceptObjectPeriod"
            ],
            "additionalProperties": False,

            "properties": {
                "description": {
                    "title": "Object description",
                    "description": "Object description (including address, object quality, etc)",
                    "type": "string",
                    "minLength": 20,
                    "maxLength": 300,
                    "pattern": "^[a-zA-Z0-9,\.\? ]+$"
                },

                "price": {
                    "title": "Price",
                    "description": "Price for rent of object for while rent period",
                    "$ref": "#/definitions/ethCountPositive"
                },
                "fileUrl": {
                    "title": "Url of file with additional description",
                    "description": "Photo, pdf, presentation",
                    "type": "string",
                    "minLength": 10,
                    "maxLength": 300
                },
                "fileHash": {
                    "title": "Hash of file above",
                    "description": "Just upload file, hash will be calculated automatically",
                    "$ref": "#/definitions/fileHash"
                },
                "cancellationFee": {
                    "title": "Cancellation fee",
                    "description": "For canceling after \"no cancel\" time",
                    "$ref": "#/definitions/ethCount"
                },
                "rentDateStart": {
                    "title": "Start rent time",
                    "$ref": "#/definitions/unixTime"
                },
                "rentDateEnd": {
                    "title": "End rent time",
                    "$ref": "#/definitions/unixTime"
                },
                "noCancelPeriod": {
                    "title": "No cancel time (in hours)",
                    "description": "After this time before start rent time cancellation fee would be collected from the customer",
                    "type": "integer"
                },
                "acceptObjectPeriod": {
                    "title": "Accept object time (in hours)",
                    "description": "Time for customer after start rent time to accept object",
                    "type": "integer"
                },

            }
        }

        ui_schema = {
            "fileHash": {
                "ui:widget": "fileHash"
            },
            "rentDateStart": {
                "ui:widget": "unixTime"
            },
            "rentDateEnd": {
                "ui:widget": "unixTime"
            }
        }

        return {
            "result": "success",
            "schema": json_schema,
            "ui_schema": ui_schema
        }

    def construct(self, fields):

        errors = {}

        if fields['price'] <= fields['cancellationFee']:
            # todo waiting for front
            return {
                "result": "error",
                "error_descr": 'Price must be greater than cancellation fee'
            }
            errors['price'] = 'Price must be greater than cancellation fee'

        if fields['rentDateStart'] < time.time():
            # todo waiting for front
            return {
                "result": "error",
                "error_descr": 'Start rent time must be in future'
            }
            errors['rentDateStart'] = 'Start rent time must be in future'

        if fields['rentDateStart'] >= fields['rentDateEnd']:
            # todo waiting for front
            return {
                "result": "error",
                "error_descr": 'Start rent time must be less than end rent time'
            }
            errors['rentDateStart'] = 'Start rent time must be less than end rent time'

        if fields['rentDateStart']+fields['acceptObjectPeriod']*60*60 >= fields['rentDateEnd']:
            # todo waiting for front
            return {
                "result": "error",
                "error_descr": 'Accept object time must be less than rent period'
            }
            errors['acceptObjectPeriod'] = 'Accept object time must be less than rent period'

        if fields['rentDateStart'] <= fields['noCancelPeriod'] * 60*60:
            # todo waiting for front
            return {
                "result": "error",
                "error_descr": '"No cancel" time must be less than start rent date'
            }
            errors['rentDateStart'] = '"No cancel" time must be less than start rent date'

        if errors:
            return {
                "result": "error",
                "errors": errors
            }

        source = self.__class__._TEMPLATE \
            .replace('%_description%', fields['description']) \
            .replace('%_price%', fields['price']) \
            .replace('%_fileUrl%', fields['fileUrl'] if 'fileUrl' in fields else '') \
            .replace('%_fileHash%', fields['fileHash'] if 'fileHash' in fields else '0') \
            .replace('%_cancellationFee%', fields['cancellationFee']) \
            .replace('%_rentDateStart%', str(fields['rentDateStart'])) \
            .replace('%_rentDateEnd%', str(fields['rentDateEnd'])) \
            .replace('%_noCancelPeriod%', str(fields['noCancelPeriod'])) \
            .replace('%_acceptObjectPeriod%', str(fields['acceptObjectPeriod']))

        return {
            "result": "success",
            'source': source,
            'contract_name': "Booking"
        }

    def post_construct(self, fields, abi_array):

        function_titles = {

            'm_client': {
                'title': 'Client address',
                'sorting_order': 5
            },

            'm_description': {
                'title': 'Object description',
                'sorting_order': 10
            },

            'm_fileUrl': {
                'title': 'Description url',
                'description': 'Url of file with additional description',
                'sorting_order': 11
            },

            'm_fileHash': {
                'title': 'Description hash',
                'description': 'Hash (keccak256) of file with additional description',
                'sorting_order': 12
            },

            'm_rentDateStart': {
                'title': 'Start rent time',
                'ui:widget': 'unixTime',
                'sorting_order': 20
            },

            'm_rentDateEnd': {
                'title': 'End rent time',
                'ui:widget': 'unixTime',
                'sorting_order': 30
            },

            'm_price': {
                'title': 'Rent price',
                'description': 'Rent price for whole period',
                'ui:widget': 'ethCount',
                'sorting_order': 40
            },

            'm_cancellationFee': {
                'title': 'Cancellation fee',
                'ui:widget': 'ethCount',
                'sorting_order': 50
            },

            'm_noCancelPeriod': {
                'title': '"No cancel" time',
                'sorting_order': 60
            },

            'm_acceptObjectPeriod': {
                'title': 'Accept object time',
                'sorting_order': 70
            },

            'getCurrentState': {
                'title': 'Get booking state',
                'ui:widget': 'enum',
                'ui:widget_options': {
                    'enum': ['Offer', 'Paid', 'No cancel period', 'Rent', 'Finished']
                },
                'sorting_order': 80
            },

            'refund': {
                'title': 'Refund (customer)',
                # 'description': 'Refund ..',
                'sorting_order': 200
            },

            'rejectPayment': {
                'title': 'Reject payment (owner)',
                # 'description': 'Reject payment ..',
                'sorting_order': 210
            },

            'cancelBooking': {
                'title': 'Cancel booking (owner)',
                # 'description': 'Cancel booking ..',
                'sorting_order': 220
            },

            'startRent': {
                'title': 'Start rent (customer)',
                # 'description': 'Start rent ..',
                'sorting_order': 230
            },

            'transferOwnership': {
                'title': 'Transfer ownership (owner)',
                'description': 'Transfer ownership of contract',
                'inputs': [{
                    'title': 'New owner address',
                }],
                'sorting_order': 240
            },
        }

        return {
            "result": "success",
            'function_specs': function_titles,
            'dashboard_functions': ['ballotName']
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
contract Booking is Ownable {

    function Booking() public payable {

        m_description = '%_description%';
        m_fileUrl = '%_fileUrl%';
        m_fileHash = %_fileHash%;
        m_price = %_price% ether;
        m_cancellationFee = %_cancellationFee% ether;
        m_rentDateStart = %_rentDateStart%;
        m_rentDateEnd = %_rentDateEnd%;
        m_noCancelPeriod = %_noCancelPeriod%;
        m_acceptObjectPeriod = %_acceptObjectPeriod%;

        assert(m_price > 0);
        assert(m_price > m_cancellationFee);
        assert(m_rentDateStart > getCurrentTime());
        assert(m_rentDateEnd > m_rentDateStart);

        assert(m_rentDateStart+m_acceptObjectPeriod*60*60 < m_rentDateEnd);
        assert(m_rentDateStart > m_noCancelPeriod*60*60);
        
        %payment_code%
    }

    /************************** STRUCTS **********************/
    enum State {OFFER, PAID, NO_CANCEL, RENT, FINISHED}

    /************************** MODIFIERS **********************/

    modifier onlyState(State _state) {
        require(getCurrentState() == _state);
        _;
    }

    modifier onlyClient() {
        require(msg.sender == m_client);
        _;
    }

    /************************** EVENTS **********************/

    event StateChanged(State newState);

    /************************** CONSTANTS **********************/

    /************************** PROPERTIES **********************/

    string public m_description;
    string public m_fileUrl;
    bytes32 public m_fileHash;


    uint256 public m_price;
    uint256 public m_cancellationFee;

    uint256 public m_rentDateStart;
    uint256 public m_rentDateEnd;

    uint256 public m_noCancelPeriod;
    uint256 public m_acceptObjectPeriod;

    address public m_client;

    State internal m_state;


    /************************** FALLBACK **********************/

    function() external payable onlyState(State.OFFER) {
        require(msg.value >= m_price);
        require(msg.sender != owner);
        require(m_rentDateStart > getCurrentTime());


        changeState(State.PAID);
        m_client = msg.sender;

        if (msg.value > m_price) {
            msg.sender.transfer(msg.value-m_price);
        }
    }
    /************************** EXTERNAL **********************/


    function rejectPayment() external onlyOwner onlyState(State.PAID) {
        refundWithoutCancellationFee();
    }


    function refund() external onlyClient onlyState(State.PAID) {
        refundWithoutCancellationFee();
    }

    function startRent() external onlyClient onlyState(State.NO_CANCEL) {
        require(getCurrentTime() > m_rentDateStart);

        changeState(State.RENT);
        owner.transfer(address(this).balance);
    }

    function cancelBooking() external onlyState(State.NO_CANCEL) {
        if (getCurrentTime() >= m_rentDateStart+m_acceptObjectPeriod*60*60) {
            require(msg.sender == owner);
        } else {
            require(msg.sender == m_client);
        }

        refundWithCancellationFee();
    }

    /************************** PUBLIC **********************/

    function getCurrentState() public view returns(State) {
        if (m_state == State.PAID) {
            if (getCurrentTime() >= m_rentDateStart - m_noCancelPeriod*60*60) {
                return State.NO_CANCEL;
            } else {
                return State.PAID;
            }
        } if (m_state == State.RENT)  {
            if (getCurrentTime() >= m_rentDateEnd) {
                return State.FINISHED;
            } else {
                return State.RENT;
            }
        } else {
            return m_state;
        }
    }

    /************************** INTERNAL **********************/


    function changeState(State _newState) internal {
        State currentState = getCurrentState();

        if (State.OFFER == _newState) {
            assert(State.PAID == currentState || State.NO_CANCEL == currentState);

        } else if (State.PAID == _newState) {
            assert(State.OFFER == currentState);
            assert(address(this).balance > 0);

        } else if (State.NO_CANCEL == _newState) {
            assert(false); // no direct change

        } else if (State.RENT == _newState) {
            assert(State.NO_CANCEL == currentState);

        } else if (State.FINISHED == _newState) {
            assert(false); // no direct change

        }

        m_state = _newState;
        StateChanged(_newState);
    }

    function getCurrentTime() internal view returns (uint256) {
        return now;
    }

    /************************** PRIVATE **********************/

    function refundWithoutCancellationFee() private  {
        address client = m_client;
        m_client = address(0);
        changeState(State.OFFER);


        client.transfer(address(this).balance);
    }

    function refundWithCancellationFee() private {
        address client = m_client;
        m_client = address(0);
        changeState(State.OFFER);

        owner.transfer(m_cancellationFee);
        client.transfer(address(this).balance);
    }

}

    """
