// SPDX-License-Identifier: GPL-3.0
pragma solidity *;

contract C {
    function f() pure public {
        assembly {
            // Presence of msize disables all Yul optimizations, including the minimal steps or
            // stack optimization that would normally be performed even with the optimizer nominally disabled.
            pop(msize())
        }
    }
}
