pragma circom 2.0.0;

// Include the SHA256 implementation from Circomlib
include "./circomlib/circuits/sha256/sha256.circom";

template hasher() {
    signal input utxo_id;
    // signal input amount;
    // signal input wallet_id;
    // signal input transaction_id;
    // signal input public_input_hash;
    signal output out[1];
    // Declare SHA256 component
    component sha256 = Sha256(1); 

    // Connect private inputs to SHA256 component
    sha256.in[0] <== utxo_id;
    // sha256.in[1] <== amount;
    // sha256.in[2] <== transaction_id;
    // sha256.in[3] <== wallet_id;

    // Connect SHA256 output to output signal
    out[0] <== sha256.out[0]; 

    // assert(out[0] == public_input_hash);
}

component main = hasher();
    