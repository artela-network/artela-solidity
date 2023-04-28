{
    // In pure Yul, optimizations are still performed in presence of msize.
    // This also applies also to optimizer steps that run when Yul optimizer is not enabled.
    let x := mload(0x2000)
    pop(msize())
}
