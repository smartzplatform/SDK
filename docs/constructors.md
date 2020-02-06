# Versions of constructor api

## version 2

- Additional key `blockchain` added to result of method `get_version`:
```python
    @abstractmethod
    def get_version(self):
        """
        Get version of constructor api. If function is not exist version 0 would be used
        Since version 1 of constructor api

        Returns: {
            "result": "success",
            "blockchain": "ethereum", # string, ethereum or eos
            "version": 2 # integer
        }

        or throws exception.
        """
        raise NotImplementedError()
```

An important thing to mention for eos contract developers: make sure that ***"contract_name"***, which is returned by `construct` method, has the same name as your contract name. 
For example, we have "hello world" contract with custom message, provided by user in smartz deploy constructor page:
```cpp
  #include <eosio/eosio.hpp>
  #include <eosio/name.hpp>

  static constexpr uint64_t token_symbol = TST;

  // contract name is "hello"
  class [[eosio::contract]] hello : public eosio::contract {
     public:
        using eosio::contract::contract;

        [[eosio::action]]
        void hi() {
           eosio::print_f("%this_param_is_filled_in_by_user%");
        }
  };
```
This contract is stored as a string class attribute (`self.__class__._TEMPLATE: str`) in an implementation of `ConstructorInstance` class.
So for the "hello world" contract our `ConstructorInstance.construct` method implementation must have the same ***contract_name*** value in its return as "hello world" contract has:
```python
  def construct(self):
	source = self.__class__._TEMPLATE \
            .replace('%this_param_is_filled_in_by_user%', fields['this_param_is_filled_in_by_user'])
        
        return {
            "result": "success",
            "source": source,
            "contract_name": "hello" # The same name as in "hello world" contract
        }
```

## version 1

- Method `get_version` added to constructor interface:
```python
    @abstractmethod
    def get_version(self):
        """
        Get version of constructor api. If function is not exist version 0 would be used
        Since version 1 of constructor api

        Returns: {
            "result": "success",
            "version": 1 # integer
        }

        or throws exception.
        """
        raise NotImplementedError()
```
- Changed format of `function_specs` in `post_construct`. Now it returns `ETHFunctionAdditionalDescriptions` (see json-schema/constructor.json):
```python
    @abstractmethod
    def post_construct(self, fields, abi_array):
        """
        Called after compiling constructed source to get extra contract info.

        :param fields: fields data provided during construct
        :param abi_array: Ethereum ABI of compiled contract
        :return: {
            "result": "success",
            "function_specs": ETHFunctionAdditionalDescriptions (see json-schema/constructor.json),
            "dashboard_functions": list of function names
        }

        Should not throw.
        """
        raise NotImplementedError()
```


## version 0 (deprecated, would not be supported after 01.05.2018)

- Constructor must implement constructor interface: `smartz.api.constructor_engine.ConstructorInstance`:
```python
class ConstructorInstance(metaclass=ABCMeta):
    """
    Constructor interface.
    """

    @abstractmethod
    def get_params(self):
        """
        Get json schema of construct() parameters.

        Returns: {
            "result": "success",
            "schema": json_schema,
            "ui_schema": ui_schema
        }

        or throws exception.
        """
        raise NotImplementedError()

    @abstractmethod
    def construct(self, fields):
        """
        Constructs contract source code.

        :param fields: data which is compatible to schema provided by get_params()

        Returns on success: {
            "result": "success",
            "source": source code string,
            "contract_name": main contract name
        }

        or on global error: {
            "result": "error",
            "error_descr": error string
        }

        or on error specific to some provided fields: {
            "result": "error",
            "errors": {
                field name: error string,
                ...
            }
        }
        """
        raise NotImplementedError()

    @abstractmethod
    def post_construct(self, fields, abi_array):
        """
        Called after compiling constructed source to get extra contract info.

        :param fields: fields data provided during construct
        :param abi_array: Ethereum ABI of compiled contract
        :return: {
            "result": "success",
            "function_specs": list of ETHFunctionSpec (see json-schema/constructor.json),
            "dashboard_functions": list of function names
        }

        Should not throw.
        """
        raise NotImplementedError()
```
