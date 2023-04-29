object "Contract" {
  code {
    function f() { g(1) }
    function g(x) { if x { leave } g(add(x, 2)) }
    g(1)
  }
}

// ====
// optimizationPreset: none
// ----
// Assembly:
//     /* "source":109:113   */
//   tag_2
//     /* "source":111:112   */
//   0x01
//     /* "source":109:113   */
//   tag_1
//   jump	// in
// tag_2:
//     /* "source":27:117   */
//   stop
//     /* "source":59:104   */
// tag_1:
//   dup1
//     /* "source":75:89   */
//   tag_3
//   jumpi
//     /* "source":73:104   */
// tag_4:
//     /* "source":99:100   */
//   0x02
//     /* "source":90:102   */
//   tag_5
//     /* "source":92:101   */
//   swap2
//   add
//     /* "source":90:102   */
//   tag_1
//   jump	// in
// tag_5:
//     /* "source":59:104   */
//   jump	// out
//     /* "source":80:89   */
// tag_3:
//     /* "source":82:87   */
//   pop
//   jump	// out
// Bytecode: 600760016009565b005b80601a575b6002601891016009565b565b5056
// Opcodes: PUSH1 0x7 PUSH1 0x1 PUSH1 0x9 JUMP JUMPDEST STOP JUMPDEST DUP1 PUSH1 0x1A JUMPI JUMPDEST PUSH1 0x2 PUSH1 0x18 SWAP2 ADD PUSH1 0x9 JUMP JUMPDEST JUMP JUMPDEST POP JUMP
// SourceMappings: 109:4:0:-:0;111:1;109:4;:::i;:::-;27:90;59:45;;75:14;;73:31;99:1;90:12;92:9;;90:12;:::i;:::-;59:45::o;80:9::-;82:5;:::o
