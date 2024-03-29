pragma circom 2.0.0;

include "./circomlib/circuits/sha256/sha256.circom";
include "./circomlib/circuits/bitify.circom";

template SHA256Hasher() {
    // Define input signals
    signal input utxo_id[8];
    signal input output_address[224];
    signal input amount[8];

    // Define hash signals
    signal input hash[256];
    signal output chash[256];
    
    // Concatenate all input arrays into a single input array
    signal input_concat[240]; // Total length of all input arrays

    // Copy utxo_id to input_concat
    for (var i = 0; i < 8; i++) {
        input_concat[i] <== utxo_id[i];
    }


    // Copy output_address to input_concat
    for (var i = 0; i < 224; i++) {
        input_concat[8 + i] <== output_address[i];
    }

    // Copy amount to input_concat
    for (var i = 0; i < 8; i++) {
        input_concat[232 + i] <== amount[i];
    }

    // Instantiate the SHA-256 component with the concatenated input array
    component sha256hasher = Sha256(240);

    // Connect input_concat to sha256hasher
    for (var i = 0; i < 240; i++) {
        sha256hasher.in[i] <== input_concat[i];
    }

    // Connect the output of SHA-256 component to the hash signals
    for (var i = 0; i < 256; i++) {
        chash[i] <== sha256hasher.out[i];
        hash[i] === chash[i];
    }
}

component main {public [hash]} = SHA256Hasher();
