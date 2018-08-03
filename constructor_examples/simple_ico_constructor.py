from smartz.api.constructor_engine import ConstructorInstance


class Constructor(ConstructorInstance):

    def get_version(self):
        return {
            "result": "success",
            "blockchain": "ethereum",
            "version": 2
        }

    def get_params(self):
        json_schema = {
            "type": "object",
            "required": ["name", "symbol", "date_start", "date_end", "rate", "hard_cap",
                         "funds_address"],
            "additionalProperties": False,

            "properties": {
                "name": {
                    "title": "Name of a token",
                    "description": "Token human-friendly name (3..100 characters, letters, digits and spaces only)",
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 100,
                    "pattern": "^[a-zA-Z0-9 ]+$"
                },

                "symbol": {
                    "title": "Token Symbol",
                    "description": "Token ticker (2..10 characters, letters and digits only)",
                    "type": "string",
                    "minLength": 2,
                    "maxLength": 10,
                    "pattern": "^[a-zA-Z0-9]+$"
                },

                "is_burnable": {
                    "type": "boolean",
                    "default": False,
                    "title": "Is token burnable?",
                    "description": "Can token holders burn their tokens?"
                },

                "date_start": {
                    "title": "Start date",
                    "description": "ICO start date and time (UTC)",
                    "$ref": "#/definitions/unixTime"
                },
                "date_end": {
                    "title": "End date",
                    "description": "ICO end date and time (UTC)",
                    "$ref": "#/definitions/unixTime"
                },

                "rate": {
                    "title": "Exchange rate",
                    "description": "Tokens to issue per 1 Ether",
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000000
                },

                "hard_cap": {
                    "title": "Hard cap",
                    "description": "Hard cap in Ether",
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000000000
                },

                "funds_address": {
                    "title": "Funds address",
                    "description": "All collected funds will be transferred to this address",
                    "$ref": "#/definitions/address"
                }
            }
        }

        ui_schema = {
            "date_start": {
                "ui:widget": "unixTime"
            },
            "date_end": {
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

        if fields["date_start"] >= fields["date_end"]:
            errors["date_start"] = 'Start date is greater or equal to end date'

        if errors:
            return {
                "result": "error",
                "errors": errors
            }

        source = self.__class__._TEMPLATE \
            .replace('%name%', fields['name']) \
            .replace('%symbol%', fields['symbol'].upper()) \
            .replace('%code_is_burnable%', ", BurnableToken" if fields['is_burnable'] else '') \
            .replace('%date_start%', str(fields['date_start'])) \
            .replace('%date_end%', str(fields['date_end'])) \
            .replace('%hard_cap%', str(fields['hard_cap'])) \
            .replace('%rate%', str(fields['rate'])) \
            .replace('%funds_address%', fields['funds_address'])

        return {
            'result': "success",
            'source': source,
            'contract_name': "ICO"
        }

    def post_construct(self, fields, abi_array):

        function_titles = {
            'daysRemaining': {
                'title': 'Days remaining',
                'description': 'Days before end of the ICO.',
            },

            'totalTokens': {
                'title': 'Total tokens',
                'description': 'Current total amount of the token. Specified in the smallest units of the token.',
            },

            'funds_address': {
                'title': 'Funds address',
                'description': 'Address to which the ICO forwards collected Ether.',
            },

            'rate': {
                'title': 'Token rate',
                'description': 'Token per Ether rate.',
            },

            'hard_cap': {
                'title': 'Hard cap',
                'description': 'Maximum Ether to be accepted by the ICO. Specified in the smallest units of Ether - wei.',
            },

            'collected': {
                'title': 'Collected wei',
                'description': 'Currently collected amount of Ether. Specified in the smallest units of Ether - wei.',
            },

            'collectedEther': {
                'title': 'Collected Ether',
                'description': 'Currently collected amount of Ether.',
            },

            'token': {
                'title': 'Token address',
                'description': 'Address of the ICO token. This address should be added to the wallets to see your tokens balance and manage them.',
            },

            'date_start': {
                'title': 'Start timestamp',
                'description': 'Unix timestamp of the start of ICO',
            },

            'date_end': {
                'title': 'End timestamp',
                'description': 'Unix timestamp of the end of ICO',
            }
        }

        return {
            "result": "success",
            'function_specs': function_titles,
            'dashboard_functions': ['collectedEther', 'totalTokens', 'daysRemaining']
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
 * @title ERC20Basic
 * @dev Simpler version of ERC20 interface
 * @dev see https://github.com/ethereum/EIPs/issues/179
 */
contract ERC20Basic {
  uint256 public totalSupply;
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
   * approve should be called when allowed[_spender] == 0. To increment
   * allowed value is better to use this function to avoid 2 calls (and wait until
   * the first transaction is mined)
   * From MonolithDAO Token.sol
   */
  function increaseApproval(address _spender, uint _addedValue) public returns (bool) {
    allowed[msg.sender][_spender] = allowed[msg.sender][_spender].add(_addedValue);
    Approval(msg.sender, _spender, allowed[msg.sender][_spender]);
    return true;
  }

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
    totalSupply = totalSupply.add(_amount);
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
        totalSupply = totalSupply.sub(_value);
        Burn(burner, _value);
    }
}

contract Token is MintableToken %code_is_burnable%
{
    string public constant name = '%name%';
    string public constant symbol = '%symbol%';
    uint8 public constant decimals = 18;

    function Token() public {

    }


}

contract ICO
{
    using SafeMath for uint256;

    Token public token;
    uint256 public collected;
    uint256 public date_start = %date_start%;
    uint256 public date_end = %date_end%;
    uint256 public hard_cap = %hard_cap% ether;
    uint256 public rate = %rate%;
    address public funds_address = address(%funds_address%);

    function ICO() public payable {
        token = new Token();
        %payment_code%
    }

    function () public payable {
        require(now >= date_start && now <= date_end && collected.add(msg.value)<hard_cap);
        token.mint(msg.sender, msg.value.mul(rate));
        funds_address.transfer(msg.value);
        collected = collected.add(msg.value);
    }

    function totalTokens() public view returns (uint) {
        return token.totalSupply();
    }

    function daysRemaining() public view returns (uint) {
        if (now > date_end) {
            return 0;
        }
        return date_end.sub(now).div(1 days);
    }

    function collectedEther() public view returns (uint) {
        return collected.div(1 ether);
    }
}


    """
