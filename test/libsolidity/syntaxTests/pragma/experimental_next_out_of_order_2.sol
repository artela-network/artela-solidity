pragma solidity ^0.8.19;

function f() pure returns (uint)
{
    return 1;
}

pragma experimental next;

struct A
{
    uint256 x;
}
// ----
// ParserError 8185: (105-111): Experimental pragma 'next' can only be set at the beginning of the source unit.
