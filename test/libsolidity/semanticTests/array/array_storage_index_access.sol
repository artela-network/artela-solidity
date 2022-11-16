contract C {
    uint[] storageArray;
    function test_indices(uint256 len) public
    {
        while (storageArray.length < len)
            storageArray.push();
        while (storageArray.length > len)
            storageArray.pop();
        for (uint i = 0; i < len; i++)
            storageArray[i] = i + 1;

        for (uint i = 0; i < len; i++)
            require(storageArray[i] == i + 1);
    }
}
// ----
// test_indices(uint256): 1 ->
// test_indices(uint256): 129 ->
// gas irOptimized: 3006907
// gas legacy: 3040723
// gas legacyOptimized: 2996871
// test_indices(uint256): 5 ->
// gas irOptimized: 577580
// gas legacy: 574361
// gas legacyOptimized: 572368
// test_indices(uint256): 10 ->
// gas irOptimized: 157277
// gas legacy: 160257
// gas legacyOptimized: 157062
// test_indices(uint256): 15 ->
// gas irOptimized: 171772
// gas legacy: 176182
// gas legacyOptimized: 171687
// test_indices(uint256): 0xFF ->
// gas irOptimized: 5652837
// gas legacy: 5719777
// gas legacyOptimized: 5634317
// test_indices(uint256): 1000 ->
// gas irOptimized: 18095919
// gas legacy: 18362799
// gas legacyOptimized: 18043744
// test_indices(uint256): 129 ->
// gas irOptimized: 4147180
// gas legacy: 4144843
// gas legacyOptimized: 4112276
// test_indices(uint256): 128 ->
// gas irOptimized: 398236
// gas legacy: 435048
// gas legacyOptimized: 401560
// test_indices(uint256): 1 ->
// gas irOptimized: 581484
// gas legacy: 577240
// gas legacyOptimized: 576059
