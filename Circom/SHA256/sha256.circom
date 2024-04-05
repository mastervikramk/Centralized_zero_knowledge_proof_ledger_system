pragma circom 2.0.0;

include "./circomlib/circuits/sha256/sha256.circom";
include "./circomlib/circuits/bitify.circom";

template SHA256Hasher() {
    // Define input signals
    signal input utxo_1[64];
    signal input utxo_2[64];
    signal input output_address[224];
    signal input amount[64];
    signal input signature[768];


    // Define hash signals
    signal input hash[256];
    signal output chash[256];
    var ut1=64,ut2=64,addr=224,amt=64,sig=768;
    
    var total=ut1+ut2+addr+amt+sig;
    // Concatenate all input arrays into a single input array
    signal input_concat[total]; // Total length of all input arrays

    // Copy utxo_id to input_concat
    for (var i = 0; i < ut1; i++) {
        input_concat[i] <== utxo_1[i];
    }

     // Copy utxo_id to input_concat
    for (var i = 0; i < ut2; i++) {
        input_concat[ut1+i] <== utxo_2[i];
    }

    // Copy output_address to input_concat
    for (var i = 0; i < addr; i++) {
        input_concat[ut1+ut2+ i] <== output_address[i];
    }

    // Copy amount to input_concat
    for (var i = 0; i < amt; i++) {
        input_concat[ut1+ut2+addr + i] <== amount[i];
    }

    // Copy amount to input_concat
    for (var i = 0; i < sig; i++) {
        input_concat[ut1+ut2+addr+amt + i] <== signature[i];
    }

    // Instantiate the SHA-256 component with the concatenated input array
    component sha256hasher = Sha256(total);

    // Connect input_concat to sha256hasher
    for (var i = 0; i < total; i++) {
        sha256hasher.in[i] <== input_concat[i];
    }

    // Connect the output of SHA-256 component to the hash signals
    for (var i = 0; i < 256; i++) {
        chash[i] <== sha256hasher.out[i];
        hash[i] === chash[i];
    }
}

component main {public [hash]} = SHA256Hasher();
