
from smartz.api.constructor_engine import ConstructorInstance
from smartz.eth.contracts import make_generic_function_spec, merge_function_titles2specs


class Constructor(ConstructorInstance):

    def get_params(self):
        json_schema = {
            "type": "object",
            "required": [
                "name", "variants"
            ],
            "additionalProperties": False,

            "properties": {
                "name": {
                    "title": "Ballot topic",
                    "description": "Name or description of the vote (string of 200 chars max)",
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 200,
                    "pattern": "^[a-zA-Z0-9,\.\? ]+$"
                },

                "variants": {
                    "title": "Variants",
                    "description": "List of answer variants. One account can vote only for one variant",
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 100,
                    "items": {
                        "title": "Variant",
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 200,
                        "pattern": "^[a-zA-Z0-9,\.\? ]+$"
                    }
                }

            }
        }

        ui_schema = {}

        return {
            "result": "success",
            "schema": json_schema,
            "ui_schema": ui_schema
        }

    def construct(self, fields):
        variants_code = ''

        for variant_id, variant in enumerate(fields['variants']):
            variants_code += """
                variants.push('{variant_descr}');variantIds[sha256('{variant_descr}')] = {variant_id};
            """.format(
                variant_descr=variant,
                variant_id=variant_id+1
            )

        source = self.__class__._TEMPLATE \
            .replace('%name%', fields['name']) \
            .replace('%variants_code%', variants_code)

        return {
            "result": "success",
            'source': source,
            'contract_name': "SimpleBallot"
        }

    def post_construct(self, fields, abi_array):

        function_titles = {
            'ballotName': {
                'title': 'Ballot topic',
                'description': 'Name or description of the vote'
            },

            'variants': {
                'title': 'View variant',
                'description': 'Get variant name by ID',
                'inputs': [{
                    'title': 'Variant ID',
                }]
            },

            'isVoted': {
                'title': 'Has address voted?',
                'description': 'Check if given address has voted',
                'inputs': [{
                    'title': 'Address to check',
                }]
            },

            'vote': {
                'title': 'Vote by ID',
                'description': 'Vote by variant ID',
                'inputs': [{
                    'title': 'Variant ID',
                }]
            },

            'voteByName': {
                'title': 'Vote by name',
                'description': 'Vote by variant name',
                'inputs': [{
                    'title': 'Variant name',
                }]
            },

            'getVotesCount': {
                'title': 'Get votes count',
                'description': 'Get votes count by variant ID',
                'inputs': [{
                    'title': 'Variant ID',
                }]
            },

            'getVotesCountByName': {
                'title': 'Get votes count',
                'description': 'Get votes count by variant name',
                'inputs': [{
                    'title': 'Variant name',
                }]
            },


            'getWinningVariantId': {
                'title': 'Winning variant ID',
                'description': 'ID of the variant with the most votes'
            },

            'getWinningVariantName': {
                'title': 'Winning variant name',
                'description': 'The name of the variant with the most votes'
            },

            'getWinningVariantVotesCount': {
                'title': 'Winning variant votes count',
                'description': 'Count of votes of the variant with the most votes'
            },
        }

        return {
            "result": "success",
            'function_specs': merge_function_titles2specs(make_generic_function_spec(abi_array), function_titles),
            'dashboard_functions': ['ballotName', 'getWinningVariantId', 'getWinningVariantName', 'getWinningVariantVotesCount']
        }


    # language=Solidity
    _TEMPLATE = """
pragma solidity ^0.4.18;

/**
 * @title Simple Ballot
 */
contract SimpleBallot {

    string public ballotName;

    string[] public variants;

    mapping(uint=>uint) votesCount;
    mapping(address=>bool) public isVoted;

    mapping(bytes32=>uint) variantIds;

    function SimpleBallot() public payable {
        ballotName = '%name%';

        variants.push(''); // for starting variants from 1 (non-programmers oriented)

        %variants_code%

        assert(variants.length <= 100);
        
        %payment_code%
    }

    modifier hasNotVoted() {
        require(!isVoted[msg.sender]);

        _;
    }

    modifier validVariantId(uint _variantId) {
        require(_variantId>=1 && _variantId<variants.length);

        _;
    }

    /**
     * Vote by variant id
     */
    function vote(uint _variantId)
        public
        validVariantId(_variantId)
        hasNotVoted
    {
        votesCount[_variantId]++;
        isVoted[msg.sender] = true;
    }

    /**
     * Vote by variant name
     */
    function voteByName(string _variantName)
        public
        hasNotVoted
    {
        uint variantId = variantIds[ sha256(_variantName) ];
        require(variantId!=0);

        votesCount[variantId]++;
        isVoted[msg.sender] = true;
    }

    /**
     * Get votes count of variant (by id)
     */
    function getVotesCount(uint _variantId)
        public
        view
        validVariantId(_variantId)
        returns (uint)
    {

        return votesCount[_variantId];
    }

    /**
     * Get votes count of variant (by name)
     */
    function getVotesCountByName(string _variantName) public view returns (uint) {
        uint variantId = variantIds[ sha256(_variantName) ];
        require(variantId!=0);

        return votesCount[variantId];
    }

    /**
     * Get winning variant ID
     */
    function getWinningVariantId() public view returns (uint id) {
        uint maxVotes = votesCount[1];
        id = 1;
        for (uint i=2; i<variants.length; ++i) {
            if (votesCount[i] > maxVotes) {
                maxVotes = votesCount[i];
                id = i;
            }
        }
    }

    /**
     * Get winning variant name
     */
    function getWinningVariantName() public view returns (string) {
        return variants[ getWinningVariantId() ];
    }

    /**
     * Get winning variant name
     */
    function getWinningVariantVotesCount() public view returns (uint) {
        return votesCount[ getWinningVariantId() ];
    }
}


    """
