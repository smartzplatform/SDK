
from smartz.api.constructor_engine import ConstructorInstance
from smartz.eth.contracts import make_generic_function_spec, merge_function_titles2specs


class Constructor(ConstructorInstance):

    def get_params(self):
        json_schema = {
            "type": "object",
            "required": [
                "mask", "decimals"
            ],
            "additionalProperties": False,

            "properties": {
                "decimals": {
                    "title": "Decimals",
                    "description": "Token decimals (0..18)",
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 18,
                    "default": 18
                },

                "mask": {
                    "type": "string",
                    "default": "0xffffffff",
                    "title": "Mask for subtokens ID",
                    "description": "Logical operation AND of subtoken ID and mask must be TRUE",
                    "pattern": "^0x[0-9a-zA-Z]{1,16}$"
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

        source = self.__class__._TEMPLATE \
            .replace('%decimals%', str(fields['decimals'])) \
            .replace('%mask%', str(fields['mask']))

        return {
            "result": "success",
            "source": source,
            "contract_name": "MultiToken"
        }

    def post_construct(self, fields, abi_array):

        function_titles = {
            'transferOwnership': {
                'title': 'Transfer ownership',
                'description': 'Transfers ownership of the token to another address. Ownership rights are required to perform some administrative operations.',
                'inputs': [{
                    'title': 'Address',
                    'description': 'Address which\'ll receive ownership rights.',
                }]
            },

            'createNewSubtoken': {
                'title': 'Create new subtoken',
                'description': 'Create new subtoken and send subtokens to address',
                'inputs': [
                    {'title': 'Token ID', },
                    {
                        'title': 'Address of owner',
                        'description': 'Address which receive all subtokens',
                    }, {
                        'title': 'Tokens count',
                        'description': 'Count of tokens will be created',
                    }
                ]
            },

            'totalSupply': {
                'title': 'Total supply',
                'description': 'Current total amount of the token. Specified in the smallest units of the token.',
                'inputs': [{
                    'title': 'Token ID',
                }]
            },

            'balanceOf': {
                'title': 'Get balance',
                'description': 'Gets the token balance of any address. Return value is specified in the smallest units of the token.',
                'inputs': [
                    {'title': 'Token ID',},
                    {'title': 'Address',}
                ]
            },

            'allowance': {
                'title': 'View allowance',
                'description': 'View amount of tokens which some token holder allowed to spend by another address.',
                'inputs': [
                    {'title': 'Token ID', },
                    {
                        'title': 'Address of owner',
                        'description': 'Address which allowed to spend his tokens.',
                    }, {
                        'title': 'Address of spender',
                        'description': 'Address which was allowed to spend tokens.',
                    }
                ]
            },

            'transfer': {
                'title': 'Transfer tokens',
                'description': 'Transfers some amount of your tokens to another address.',
                'inputs': [
                    {'title': 'Token ID', },
                    {
                        'title': 'To',
                        'description': 'Recipient address.',
                    }, {
                        'title': 'Amount',
                        'description': 'Amount must be specified in the smallest units of the token.',
                    }
                ]
            },

            'transferFrom': {
                'title': 'Transfer from',
                'description': 'Transfers from one account to another. Account which tokens are transferred has to approve this spending.',
                'inputs': [
                    {'title': 'Token ID', },
                    {
                        'title': 'From',
                        'description': 'Subtract tokens from this account.',
                    }, {
                        'title': 'To',
                        'description': 'Transfer tokens to this account.',
                    }, {
                        'title': 'Amount',
                        'description': 'Amount must be specified in the smallest units of the token.',
                    }
                ]
            },

            'approve': {
                'title': 'Approve spending',
                'description': 'Allow some amount of your tokens to be spent by specified address.',
                'inputs': [
                    {'title': 'Token ID', },
                    {
                        'title': 'Address',
                        'description': 'Address to allow to spend tokens.',
                    }, {
                        'title': 'Amount',
                        'description': 'Amount must be specified in the smallest units of the token.',
                    }
                ]
            },

        }

        return {
            "result": "success",
            'function_specs': merge_function_titles2specs(make_generic_function_spec(abi_array), function_titles),
            'dashboard_functions': []
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
contract MultiTokenBasics {

    function totalSupply(uint256 _tokenId) public view returns (uint256);

    function balanceOf(uint256 _tokenId, address _owner) public view returns (uint256);

    function allowance(uint256 _tokenId, address _owner, address _spender) public view returns (uint256);

    function transfer(uint256 _tokenId, address _to, uint256 _value) public returns (bool);

    function transferFrom(uint256 _tokenId, address _from, address _to, uint256 _value) public returns (bool);

    function approve(uint256 _tokenId, address _spender, uint256 _value) public returns (bool);


    event Transfer(uint256 indexed tokenId, address indexed from, address indexed to, uint256 value);
    event Approval(uint256 indexed tokenId, address indexed owner, address indexed spender, uint256 value);

}

contract MultiToken is Ownable, MultiTokenBasics {
    using SafeMath for uint256;

    mapping(uint256 => mapping(address => mapping(address => uint256))) private allowed;
    mapping(uint256 => mapping(address => uint256)) private balance;
    mapping(uint256 => uint256) private totalSupply_;


    uint8 public decimals = 18;
    uint256 public mask = 0xffffffff;



    /**
    * @dev Throws if _tokenId not exists
    * @param _tokenId uint256 is subtoken identifier
    */

    modifier existingToken(uint256 _tokenId) {
        require(totalSupply_[_tokenId] > 0 && (_tokenId & mask == _tokenId));
        _;
    }

    /**
    * @dev Throws if  _tokenId exists
    * @param _tokenId uint256 is subtoken identifier
    */

    modifier notExistingToken(uint256 _tokenId) {
        require(totalSupply_[_tokenId] == 0 && (_tokenId & mask == _tokenId));
        _;
    }





    /**
    * @dev create new subtoken with unique tokenId
    * @param _tokenId uint256 is subtoken identifier
    * @param _to The address to transfer to.
    * @param _value The amount to be transferred.
    * @return uint256 representing the total amount of tokens
    */

    function createNewSubtoken(uint256 _tokenId, address _to, uint256 _value) notExistingToken(_tokenId) onlyOwner() public returns (bool) {
        require(_value > 0);
        balance[_tokenId][_to] = _value;
        totalSupply_[_tokenId] = _value;
        Transfer(_tokenId, address(0), _to, _value);
        return true;
    }


    /**
    * @dev Gets the total amount of tokens stored by the contract
    * @param _tokenId uint256 is subtoken identifier
    * @return uint256 representing the total amount of tokens
    */

    function totalSupply(uint256 _tokenId) existingToken(_tokenId) public view returns (uint256) {
        return totalSupply_[_tokenId];
    }

    /**
    * @dev Gets the balance of the specified address
    * @param _tokenId uint256 is subtoken identifier
    * @param _owner address to query the balance of
    * @return uint256 representing the amount owned by the passed address
    */

    function balanceOf(uint256 _tokenId, address _owner) existingToken(_tokenId) public view returns (uint256) {
        return balance[_tokenId][_owner];
    }



    /**
    * @dev Function to check the amount of tokens that an owner allowed to a spender.
    * @param _tokenId uint256 is subtoken identifier
    * @param _owner address The address which owns the funds.
    * @param _spender address The address which will spend the funds.
    * @return A uint256 specifying the amount of tokens still available for the spender.
    */

    function allowance(uint256 _tokenId, address _owner, address _spender) existingToken(_tokenId) public view returns (uint256) {
        return allowed[_tokenId][_owner][_spender];
    }



    /**
    * @dev transfer token for a specified address
    * @param _tokenId uint256 is subtoken identifier
    * @param _to The address to transfer to.
    * @param _value The amount to be transferred.
    */

    function transfer(uint256 _tokenId, address _to, uint256 _value) existingToken(_tokenId) public returns (bool) {
        require(_to != address(0));
        var _sender = msg.sender;
        var balances = balance[_tokenId];
        require(_to != address(0));
        require(_value <= balances[_sender]);

        // SafeMath.sub will throw if there is not enough balance.
        balances[_sender] = balances[_sender].sub(_value);
        balances[_to] = balances[_to].add(_value);
        Transfer(_tokenId, _sender, _to, _value);
        return true;
    }


    /**
    * @dev Transfer tokens from one address to another
    * @param _tokenId uint256 is subtoken identifier
    * @param _from address The address which you want to send tokens from
    * @param _to address The address which you want to transfer to
    * @param _value uint256 the amount of tokens to be transferred
    */

    function transferFrom(uint256 _tokenId, address _from, address _to, uint256 _value) existingToken(_tokenId) public returns (bool) {
        address _sender = msg.sender;
        var balances = balance[_tokenId];
        var tokenAllowed = allowed[_tokenId];

        require(_to != address(0));
        require(_value <= balances[_from]);
        require(_value <= tokenAllowed[_from][_sender]);

        balances[_from] = balances[_from].sub(_value);
        balances[_to] = balances[_to].add(_value);
        tokenAllowed[_from][_sender] = tokenAllowed[_from][_sender].sub(_value);
        Transfer(_tokenId, _from, _to, _value);
        return true;
    }



    /**
    * @dev Approve the passed address to spend the specified amount of tokens on behalf of msg.sender.
    *
    * Beware that changing an allowance with this method brings the risk that someone may use both the old
    * and the new allowance by unfortunate transaction ordering. One possible solution to mitigate this
    * race condition is to first reduce the spender's allowance to 0 and set the desired value afterwards:
    * https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
    * @param _tokenId uint256 is subtoken identifier
    * @param _spender The address which will spend the funds.
    * @param _value The amount of tokens to be spent.
    */



    function approve(uint256 _tokenId, address _spender, uint256 _value) public returns (bool) {
        var _sender = msg.sender;
        allowed[_tokenId][_sender][_spender] = _value;
        Approval(_tokenId, _sender, _spender, _value);
        return true;
    }


}

    """
