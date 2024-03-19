pragma circom 2.0.0;

include "./circomlib/circuits/sha256/sha256.circom";

template Num2Bits(n) {
    signal input bytes[n];
    signal output out[n * 8]; // Each byte will be converted to 8 bits
    var e2 = 1;
    for (var i = 0; i < n; i++) {
        for (var j = 0; j < 8; j++) { // Loop over each bit in the byte
            out[i * 8 + j] <-- (bytes[i] >> j) & 1;
            out[i * 8 + j] * (out[i * 8 + j] - 1) === 0;
            e2 = e2 + e2;
        }
    }
}

template secret(){
     signal input secretInput[8];
     signal input publicInputHash[256];
     signal outputHash[256];


    component secretBits=Num2Bits(8);
    
    for (var i = 0; i < 8; i++) {
        secretBits.bytes[i] <== secretInput[i];
    }

     component SHA=Sha256(64);
     SHA.in <==secretBits.out;
     outputHash<== SHA.out;

  
   outputHash === publicInputHash;
     

}

component main{public[publicInputHash]} = secret();
