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
                "name", "symbol", "decimals", #"is_mintable", #"max_tokens_count",
                #"premint", # "premint_address",
                #"is_burnable", "is_pausable",
                #"is_circulation_restricted"
            ],
            "additionalProperties": False,

            "properties": {
                "name": {
                    "title": "Name of a token",
                    "description": "Public token human-friendly name (3..100 characters, letters, digits and spaces only).",
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 100,
                    "pattern": "^[a-zA-Z0-9 ]+$"
                },

                "symbol": {
                    "title": "Token Symbol",
                    "description": "Token ticker, like BTC or ETH (2..10 characters, letters and digits only).",
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 10,
                    "pattern": "^[a-zA-Z0-9]+$"
                },

                "decimals": {
                    "title": "Decimals",
                    "description": "Token decimal places, determines the size of smallest quantum of your token (0..18).",
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 18
                },

                "is_mintable": {
                    "type": "boolean",
                    "default": False,
                    "title": "Is token mintable?",
                    "description": "If checked, token owner can mint new tokens up to Maximum value of issue."
                },

                "max_tokens_count": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 2**63,
                    "default": 100,
                    "title": "Maximun value of issue",
                    "description": "Maximum possible number of existing tokens. Matters only for mintable tokens. Leave blank for unlimited."
                },

                "premint": {
                    "type": "integer",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 2 ** 63,
                    "title": "Premint tokens",
                    "description": "How many tokens to premint and give to owner (you) right after deploy. For not mintable tokens this is the only way to create tokens at all. Leave blank to skip preminting."
                },


                "is_burnable": {
                    "type": "boolean",
                    "default": False,
                    "title": "Is token burnable?",
                    "description": "If checked, any token holder can explicitly burn his tokens by special transaction."
                },

                "is_pausable": {
                    "type": "boolean",
                    "default": False,
                    "title": "Is token pausable?",
                    "description": "If checked, token owner can pause all token functions for a while."
                },

            }
        }

        ui_schema = {}

        return {
            "result": "success",
            "schema": json_schema,
            "ui_schema": ui_schema
        }

    def construct(self, fields):
        errors = {}

        # if fields["date_start"] >= fields["date_end"]:
        #     errors["date_start"] = 'Start date is greater or equal to end date'



        parents_code = ''
        constructors_code = ''
        if fields['is_mintable']:
            parents_code+=', MintableToken'
            if 'max_tokens_count' in fields and fields['max_tokens_count']:
                parents_code+=', CappedToken'
                constructors_code+=' CappedToken({}*10**uint(decimals))'.format(fields['max_tokens_count'])

        if fields['is_burnable']:
            parents_code+=', BurnableToken'

        if fields['is_pausable']:
            parents_code+=', PausableToken'

        constructor_inner_code = ''
        if 'premint' in fields and fields['premint']:
            constructor_inner_code = """
                uint premintAmount = {}*10**uint(decimals);
                totalSupply_ = totalSupply_.add(premintAmount);
                balances[msg.sender] = balances[msg.sender].add(premintAmount);
                Transfer(address(0), msg.sender, premintAmount);

            """.format(fields['premint'])


        if errors:
            return {
                "result": "error",
                "errors": errors
            }

        source = self.__class__._TEMPLATE \
            .replace('%name%', fields['name']) \
            .replace('%symbol%', fields['symbol'].upper()) \
            .replace('%decimals%', str(fields['decimals'])) \
            .replace('%parents_code%', parents_code) \
            .replace('%constructors_code%', constructors_code) \
            .replace('%constructor_inner_code%', constructor_inner_code)

        return {
            "result": "success",
            "source": source,
            "contract_name": "Token"
        }

    def post_construct(self, fields, abi_array):

        function_titles = {
            #
            # VIEW functions
            #
            'name': {
                'title': 'Token name',
                'description': 'Human-friendly name of the token.',
                'sorting_order': 10,
            },

            'symbol': {
                'title': 'Token ticker',
                'description': 'Abbreviated name of the token used on exchanges etc.',
                'sorting_order': 20,
            },

            'decimals': {
                'title': 'Decimal places',
                'description': 'Allowed digits in fractional part of the token. E.g. decimal places of US dollar is 2.',
                'sorting_order': 30,
            },

            'totalSupply': {
                'title': 'Total supply',
                'description': 'Current total amount of the token. Specified in the smallest units of the token.',
                'sorting_order': 40,
            },

            'cap': {
                'title': 'Maximun value of issue',
                'description': 'Maximum number of tokens which could be created. Return value is specified in the smallest units of the token.',
                'sorting_order': 50,
            },

            'mintingFinished': {
                'title': 'Minting finished',
                'description': 'If true, no more tokens could be created.',
                'sorting_order': 60,
            },

            'paused': {
                'title': 'Paused',
                'description': 'If true, all token functions are disabled.',
                'sorting_order': 70,
            },

            'owner': {
                'title': 'Owner',
                'description': 'Address of the token owner.',
                'sorting_order': 80,
            },

            #
            # ASK functions
            #
            'balanceOf': {
                'title': 'Get balance',
                'description': 'Gets the token balance of any address. Return value is specified in the smallest units of the token.',
                'inputs': [{
                    'title': 'Address',
                }],
                'sorting_order': 110,
                'icon': {
                    'pack': 'materialdesignicons',
                    'name': 'wallet'
                },
            },

            'allowance': {
                'title': 'View allowance',
                'description': 'View amount of tokens which some token holder allowed to spend by another address.',
                'inputs': [{
                    'title': 'Address of owner',
                    'description': 'Address which allowed to spend his tokens.',
                }, {
                    'title': 'Address of spender',
                    'description': 'Address which was allowed to spend tokens.',
                }],
                'sorting_order': 110,
                'icon': {
                    'pack': 'materialdesignicons',
                    'name': 'lock-question'
                },
            },

            #
            # WRITE functions
            #
            'transfer': {
                'title': 'Transfer tokens',
                'description': 'Transfers some amount of your tokens to another address.',
                'inputs': [{
                    'title': 'To',
                    'description': 'Recipient address.',
                }, {
                    'title': 'Amount',
                    'description': 'Amount should be specified in the smallest units of the token.',
                }],
                'sorting_order': 210,
                'icon': {
                    'pack': 'materialdesignicons',
                    'name': 'arrow-right'
                },

            },

            'transferFrom': {
                'title': 'Transfer from',
                'description': 'Transfers from one account to another. Account which tokens are transferred has to approve this spending.',
                'inputs': [{
                    'title': 'From',
                    'description': 'Subtract tokens from this account.',
                }, {
                    'title': 'To',
                    'description': 'Transfer tokens to this account.',
                }, {
                    'title': 'Amount',
                    'description': 'Amount should be specified in the smallest units of the token.',
                }],
                'sorting_order': 220,
                'icon': {
                    'pack': 'materialdesignicons',
                    'name': 'arrow-expand-right'
                },

            },

            'approve': {
                'title': 'Approve spending',
                'description': 'Allow some amount of your tokens to be spent by specified address.',
                'inputs': [{
                    'title': 'Address',
                    'description': 'Address to allow to spend tokens.',
                }, {
                    'title': 'Amount',
                    'description': 'Amount should be specified in the smallest units of the token.',
                }],
                'sorting_order': 230,
                'icon': {
                    'pack': 'materialdesignicons',
                    'name': 'approval'
                },

            },

            'increaseApproval': {
                'title': 'Increase approval',
                'description': 'Increases amount of your tokens which are allowed to be spent by specified address.',
                'inputs': [{
                    'title': 'Address',
                    'description': 'Address which was allowed to spend tokens.',
                }, {
                    'title': 'Amount',
                    'description': 'Amount must be specified in the smallest units of the token.',
                }],
                'sorting_order': 240,
                'icon': {
                    'pack': 'materialdesignicons',
                    'name': 'arrow-up-bold-circle-outline'
                },

            },

            'decreaseApproval': {
                'title': 'Decrease approval',
                'description': 'Decreases amount of your tokens which are allowed to be spent by specified address.',
                'inputs': [{
                    'title': 'Address',
                    'description': 'Address which was allowed to spend tokens.',
                }, {
                    'title': 'Amount',
                    'description': 'Amount must be specified in the smallest units of the token.',
                }],
                'sorting_order': 250,
                'icon': {
                    'pack': 'materialdesignicons',
                    'name': 'arrow-down-bold-circle-outline'
                },

            },

            'burn': {
                'title': 'Burn tokens',
                'description': 'Burns specified amount of tokens owned by current account.',
                'inputs': [{
                    'title': 'Amount',
                    'description': 'Amount must be specified in the smallest units of the token.'
                }],
                'sorting_order': 260,
                'icon': {
                    'pack': 'materialdesignicons',
                    'name': 'fire'
                },

            },

            'pause': {
                'title': 'Pause circulation',
                'description': 'Disable any token transfers. Callable only by token owner.',
                'sorting_order': 270,
                'icon': {
                    'pack': 'materialdesignicons',
                    'name': 'pause'
                },

            },

            'unpause': {
                'title': 'Enable circulation',
                'description': 'Enables token transfers in case they were paused. Callable only by token owner.',
                'sorting_order': 280,
                'icon': {
                    'pack': 'materialdesignicons',
                    'name': 'play'
                },

            },

            'mint': {
                'title': 'Mint new tokens',
                'description': 'Creates new tokens out-of-thin-air and gives them to specified address. Callable only by token owner.',
                'inputs': [{
                    'title': 'Address',
                    'description': 'Transfer tokens to this address.',
                }, {
                    'title': 'Amount',
                    'description': 'Amount must be specified in the smallest units of the token.',
                }],
                'sorting_order': 290,
                'icon': {
                    'pack': 'materialdesignicons',
                    'name': 'coins'
                },

            },

            'finishMinting': {
                'title': 'Finish minting',
                'description': 'Disables any further token creation via minting. Callable only by token owner.',
                'sorting_order': 300,
                'icon': {
                    'pack': 'materialdesignicons',
                    'name': 'stop'
                },

            },

            'transferOwnership': {
                'title': 'Transfer ownership',
                'description': 'Transfers ownership of the token to another address. Ownership rights are required to perform some administrative operations.',
                'inputs': [{
                    'title': 'Address',
                    'description': 'Address which\'ll receive ownership rights.',
                }],
                'sorting_order': 310,
                'icon': {
                    'pack': 'materialdesignicons',
                    'name': 'account-switch'
                },

            }
        }

        return {
            "result": "success",
            'function_specs': function_titles,
            'dashboard_functions': ['name', 'symbol', 'decimals', 'totalSupply']
        }


    # language=Solidity
    _TEMPLATE = """
pragma solidity ^0.4.18;


/**
 * @title SafeMath
 * @dev Math operations with safety checks that throw on error
 */
library SafeMath {
  function mul(uint256 a, uint256 b) internal pure returns (uint256) {
    if (a == 0) {
      return 0;
    }
    uint256 c = a * b;
    assert(c / a == b);
    return c;
  }

  function div(uint256 a, uint256 b) internal pure returns (uint256) {
    // assert(b > 0); // Solidity automatically throws when dividing by 0
    uint256 c = a / b;
    // assert(a == b * c + a % b); // There is no case in which this doesn't hold
    return c;
  }

  function sub(uint256 a, uint256 b) internal pure returns (uint256) {
    assert(b <= a);
    return a - b;
  }

  function add(uint256 a, uint256 b) internal pure returns (uint256) {
    uint256 c = a + b;
    assert(c >= a);
    return c;
  }
}


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
 * @title ERC20Basic
 * @dev Simpler version of ERC20 interface
 * @dev see https://github.com/ethereum/EIPs/issues/179
 */
contract ERC20Basic {
  function totalSupply() public view returns (uint256);
  function balanceOf(address who) public view returns (uint256);
  function transfer(address to, uint256 value) public returns (bool);
  event Transfer(address indexed from, address indexed to, uint256 value);
}

/**
 * @title ERC20 interface
 * @dev see https://github.com/ethereum/EIPs/issues/20
 */
contract ERC20 is ERC20Basic {
  function allowance(address owner, address spender) public view returns (uint256);
  function transferFrom(address from, address to, uint256 value) public returns (bool);
  function approve(address spender, uint256 value) public returns (bool);
  event Approval(address indexed owner, address indexed spender, uint256 value);
}


/**
 * @title Basic token
 * @dev Basic version of StandardToken, with no allowances.
 */
contract BasicToken is ERC20Basic {
  using SafeMath for uint256;

  mapping(address => uint256) balances;

  uint256 totalSupply_;

  /**
  * @dev total number of tokens in existence
  */
  function totalSupply() public view returns (uint256) {
    return totalSupply_;
  }

  /**
  * @dev transfer token for a specified address
  * @param _to The address to transfer to.
  * @param _value The amount to be transferred.
  */
  function transfer(address _to, uint256 _value) public returns (bool) {
    require(_to != address(0));
    require(_value <= balances[msg.sender]);

    // SafeMath.sub will throw if there is not enough balance.
    balances[msg.sender] = balances[msg.sender].sub(_value);
    balances[_to] = balances[_to].add(_value);
    Transfer(msg.sender, _to, _value);
    return true;
  }

  /**
  * @dev Gets the balance of the specified address.
  * @param _owner The address to query the the balance of.
  * @return An uint256 representing the amount owned by the passed address.
  */
  function balanceOf(address _owner) public view returns (uint256 balance) {
    return balances[_owner];
  }

}


/**
 * @title Standard ERC20 token
 *
 * @dev Implementation of the basic standard token.
 * @dev https://github.com/ethereum/EIPs/issues/20
 * @dev Based on code by FirstBlood: https://github.com/Firstbloodio/token/blob/master/smart_contract/FirstBloodToken.sol
 */
contract StandardToken is ERC20, BasicToken {

  mapping (address => mapping (address => uint256)) internal allowed;


  /**
   * @dev Transfer tokens from one address to another
   * @param _from address The address which you want to send tokens from
   * @param _to address The address which you want to transfer to
   * @param _value uint256 the amount of tokens to be transferred
   */
  function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
    require(_to != address(0));
    require(_value <= balances[_from]);
    require(_value <= allowed[_from][msg.sender]);

    balances[_from] = balances[_from].sub(_value);
    balances[_to] = balances[_to].add(_value);
    allowed[_from][msg.sender] = allowed[_from][msg.sender].sub(_value);
    Transfer(_from, _to, _value);
    return true;
  }

  /**
   * @dev Approve the passed address to spend the specified amount of tokens on behalf of msg.sender.
   *
   * Beware that changing an allowance with this method brings the risk that someone may use both the old
   * and the new allowance by unfortunate transaction ordering. One possible solution to mitigate this
   * race condition is to first reduce the spender's allowance to 0 and set the desired value afterwards:
   * https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
   * @param _spender The address which will spend the funds.
   * @param _value The amount of tokens to be spent.
   */
  function approve(address _spender, uint256 _value) public returns (bool) {
    allowed[msg.sender][_spender] = _value;
    Approval(msg.sender, _spender, _value);
    return true;
  }

  /**
   * @dev Function to check the amount of tokens that an owner allowed to a spender.
   * @param _owner address The address which owns the funds.
   * @param _spender address The address which will spend the funds.
   * @return A uint256 specifying the amount of tokens still available for the spender.
   */
  function allowance(address _owner, address _spender) public view returns (uint256) {
    return allowed[_owner][_spender];
  }

  /**
   * @dev Increase the amount of tokens that an owner allowed to a spender.
   *
   * approve should be called when allowed[_spender] == 0. To increment
   * allowed value is better to use this function to avoid 2 calls (and wait until
   * the first transaction is mined)
   * From MonolithDAO Token.sol
   * @param _spender The address which will spend the funds.
   * @param _addedValue The amount of tokens to increase the allowance by.
   */
  function increaseApproval(address _spender, uint _addedValue) public returns (bool) {
    allowed[msg.sender][_spender] = allowed[msg.sender][_spender].add(_addedValue);
    Approval(msg.sender, _spender, allowed[msg.sender][_spender]);
    return true;
  }

  /**
   * @dev Decrease the amount of tokens that an owner allowed to a spender.
   *
   * approve should be called when allowed[_spender] == 0. To decrement
   * allowed value is better to use this function to avoid 2 calls (and wait until
   * the first transaction is mined)
   * From MonolithDAO Token.sol
   * @param _spender The address which will spend the funds.
   * @param _subtractedValue The amount of tokens to decrease the allowance by.
   */
  function decreaseApproval(address _spender, uint _subtractedValue) public returns (bool) {
    uint oldValue = allowed[msg.sender][_spender];
    if (_subtractedValue > oldValue) {
      allowed[msg.sender][_spender] = 0;
    } else {
      allowed[msg.sender][_spender] = oldValue.sub(_subtractedValue);
    }
    Approval(msg.sender, _spender, allowed[msg.sender][_spender]);
    return true;
  }

}



/**
 * @title Mintable token
 * @dev Simple ERC20 Token example, with mintable token creation
 * @dev Issue: * https://github.com/OpenZeppelin/zeppelin-solidity/issues/120
 * Based on code by TokenMarketNet: https://github.com/TokenMarketNet/ico/blob/master/contracts/MintableToken.sol
 */
contract MintableToken is StandardToken, Ownable {
  event Mint(address indexed to, uint256 amount);
  event MintFinished();

  bool public mintingFinished = false;


  modifier canMint() {
    require(!mintingFinished);
    _;
  }

  /**
   * @dev Function to mint tokens
   * @param _to The address that will receive the minted tokens.
   * @param _amount The amount of tokens to mint.
   * @return A boolean that indicates if the operation was successful.
   */
  function mint(address _to, uint256 _amount) onlyOwner canMint public returns (bool) {
    totalSupply_ = totalSupply_.add(_amount);
    balances[_to] = balances[_to].add(_amount);
    Mint(_to, _amount);
    Transfer(address(0), _to, _amount);
    return true;
  }

  /**
   * @dev Function to stop minting new tokens.
   * @return True if the operation was successful.
   */
  function finishMinting() onlyOwner canMint public returns (bool) {
    mintingFinished = true;
    MintFinished();
    return true;
  }
}

/**
 * @title Capped token
 * @dev Mintable token with a token cap.
 */
contract CappedToken is MintableToken {

  uint256 public cap;

  function CappedToken(uint256 _cap) public {
    require(_cap > 0);
    cap = _cap;
  }

  /**
   * @dev Function to mint tokens
   * @param _to The address that will receive the minted tokens.
   * @param _amount The amount of tokens to mint.
   * @return A boolean that indicates if the operation was successful.
   */
  function mint(address _to, uint256 _amount) onlyOwner canMint public returns (bool) {
    require(totalSupply_.add(_amount) <= cap);

    return super.mint(_to, _amount);
  }

}



/**
 * @title Burnable Token
 * @dev Token that can be irreversibly burned (destroyed).
 */
contract BurnableToken is BasicToken {

  event Burn(address indexed burner, uint256 value);

  /**
   * @dev Burns a specific amount of tokens.
   * @param _value The amount of token to be burned.
   */
  function burn(uint256 _value) public {
    require(_value <= balances[msg.sender]);
    // no need to require value <= totalSupply, since that would imply the
    // sender's balance is greater than the totalSupply, which *should* be an assertion failure

    address burner = msg.sender;
    balances[burner] = balances[burner].sub(_value);
    totalSupply_ = totalSupply_.sub(_value);
    Burn(burner, _value);
  }
}



/**
 * @title Pausable
 * @dev Base contract which allows children to implement an emergency stop mechanism.
 */
contract Pausable is Ownable {
  event Pause();
  event Unpause();

  bool public paused = false;


  /**
   * @dev Modifier to make a function callable only when the contract is not paused.
   */
  modifier whenNotPaused() {
    require(!paused);
    _;
  }

  /**
   * @dev Modifier to make a function callable only when the contract is paused.
   */
  modifier whenPaused() {
    require(paused);
    _;
  }

  /**
   * @dev called by the owner to pause, triggers stopped state
   */
  function pause() onlyOwner whenNotPaused public {
    paused = true;
    Pause();
  }

  /**
   * @dev called by the owner to unpause, returns to normal state
   */
  function unpause() onlyOwner whenPaused public {
    paused = false;
    Unpause();
  }
}

/**
 * @title Pausable token
 * @dev StandardToken modified with pausable transfers.
 **/
contract PausableToken is StandardToken, Pausable {

  function transfer(address _to, uint256 _value) public whenNotPaused returns (bool) {
    return super.transfer(_to, _value);
  }

  function transferFrom(address _from, address _to, uint256 _value) public whenNotPaused returns (bool) {
    return super.transferFrom(_from, _to, _value);
  }

  function approve(address _spender, uint256 _value) public whenNotPaused returns (bool) {
    return super.approve(_spender, _value);
  }

  function increaseApproval(address _spender, uint _addedValue) public whenNotPaused returns (bool success) {
    return super.increaseApproval(_spender, _addedValue);
  }

  function decreaseApproval(address _spender, uint _subtractedValue) public whenNotPaused returns (bool success) {
    return super.decreaseApproval(_spender, _subtractedValue);
  }
}

contract Token is StandardToken %parents_code% {

    string public constant name = '%name%';
    string public constant symbol = '%symbol%';
    uint8 public constant decimals = %decimals%;

    function Token()
        public
        payable
        %constructors_code%
    {
        %constructor_inner_code%
        %payment_code%
    }

}


    """
