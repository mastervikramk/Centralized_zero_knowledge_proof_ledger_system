pragma circom 2.0.0;

include "./circomlib/circuits/sha256/sha256.circom";
include "./circomlib/circuits/bitify.circom";

template secret() {
    signal input secretInput;
    signal input publicInputHash[256];
    signal output outputHash[256];

    component bits = Num2Bits(1);
  
    bits.in <== secretInput;
   
    component SHA = Sha256(1);
  
    SHA.in <== bits.out;


    for(var k=0;k<256;k++){
    outputHash[k] <== SHA.out[k];}
    
    
    for( var i=0;i<256;i++){
    outputHash[i] === publicInputHash[i];}
}

component main {public [publicInputHash]} = secret();

