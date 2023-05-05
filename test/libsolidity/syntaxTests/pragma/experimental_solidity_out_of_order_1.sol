pragma solidity ^0.8.19;

contract A {}

pragma experimental solidity;
// ----
// ParserError 8185: (71-71): Experimental pragma "solidity" can only be set at the beginning of the source unit.
