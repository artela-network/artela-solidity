pragma solidity ^0.8.19;

function f() pure returns (uint)
{
    return 1;
}

pragma experimental solidity;

struct A
{
    uint256 x;
}
// ----
// ParserError 8185: (109-115): Experimental pragma "solidity" can only be set at the beginning of the source unit.
