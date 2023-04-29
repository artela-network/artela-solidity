object "Contract" {
  code {
    function f() {}
    function g() {}
    sstore(0, 1)
  }
}

// ====
// optimizationPreset: none
// ----
// Assembly:
//     /* "source":83:84   */
//   0x01
//     /* "source":80:81   */
//   0x00
//     /* "source":73:85   */
//   sstore
//     /* "source":27:89   */
//   stop
// Bytecode: 600160005500
// Opcodes: PUSH1 0x1 PUSH1 0x0 SSTORE STOP
// SourceMappings: 83:1:0:-:0;80;73:12;27:62
