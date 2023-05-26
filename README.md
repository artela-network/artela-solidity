# Artela SOLC

SOLC with Artela's enhancement, it will generate extra instructions for state modification, Aspect developer can monitor smart contracts state changes with this extra information. 

## How to build

```
mkdir build
cd build
cmake .. && make
```

## How to use

```
solc --via-ir --optimize --bin /PATH/TO/CONTRACT/mycontract.sol
```

## Issues

- Currently we only support compile with `--via-ir`, non-ir mode will be supported later
- Currently state variable with struct type are not supported

