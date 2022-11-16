contract C {
    uint256[] storageArray;
    function pushEmpty(uint256 len) public {
        while(storageArray.length < len)
            storageArray.push();

        for (uint i = 0; i < len; i++)
            require(storageArray[i] == 0);
    }
}
// ====
// EVMVersion: >=petersburg
// ----
// pushEmpty(uint256): 128
// gas irOptimized: 403598
// gas legacy: 401543
// gas legacyOptimized: 389576
// pushEmpty(uint256): 256
// gas irOptimized: 687426
// gas legacy: 686395
// gas legacyOptimized: 672764
// pushEmpty(uint256): 38869 -> FAILURE # out-of-gas #
// gas irOptimized: 100000000
// gas legacy: 100000000
// gas legacyOptimized: 100000000
