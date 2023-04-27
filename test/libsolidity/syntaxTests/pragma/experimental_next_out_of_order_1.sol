pragma solidity ^0.8.19;

contract A {}

pragma experimental next;
// ----
// ParserError 8185: (67-67): Experimental pragma 'next' can only be set at the beginning of the source unit.
