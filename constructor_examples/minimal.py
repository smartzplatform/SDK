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
            "additionalProperties": False,
        }

        return {
            "result": "success",
            "schema": json_schema,
            "ui_schema": {}
        }

    def construct(self, fields):
        return {
            "result": "success",
            "source": self.__class__._TEMPLATE,
            "contract_name": "Minimal"
        }

    def post_construct(self, fields, abi_array):

        return {
            "result": "success",
            'function_specs': {},
            'dashboard_functions': []
        }


    # language=Solidity
    _TEMPLATE = """
pragma solidity ^0.4.20;

contract Minimal {
  
  function get42() public view returns (uint) {
    return 42;
  }
  
  function() public payable {
  }

}

    """
