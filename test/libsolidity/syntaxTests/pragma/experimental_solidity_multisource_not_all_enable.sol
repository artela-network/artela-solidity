==== Source: A.sol ====
contract A {}
==== Source: B.sol ====
pragma experimental solidity;
import "A.sol";
contract B {
    A a;
}
==== Source: C.sol ====
pragma experimental solidity;
import "A.sol";
contract C {
    A a;
}
==== Source: D.sol ====
pragma experimental solidity;
import "A.sol";
contract D {
    A a;
}
// ----
// ParserError 2141: (B.sol:0-29): File declares "pragma solidity solidity". If you want to enable the experimental mode, all source units must include the pragma.
// ParserError 2141: (C.sol:0-29): File declares "pragma solidity solidity". If you want to enable the experimental mode, all source units must include the pragma.
// ParserError 2141: (D.sol:0-29): File declares "pragma solidity solidity". If you want to enable the experimental mode, all source units must include the pragma.
// Warning 2264: (B.sol:0-29): Experimental features are turned on. Do not use experimental features on live deployments.
// Warning 2264: (C.sol:0-29): Experimental features are turned on. Do not use experimental features on live deployments.
// Warning 2264: (D.sol:0-29): Experimental features are turned on. Do not use experimental features on live deployments.
