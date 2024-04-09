pragma circom 2.0.0;

include "./circomlib/circuits/poseidon.circom";

template hasher() {
    signal input input_utxo1[8];
    signal input input_utxo2[8];
    // signal input output_utxo1[8];
    // signal input output_utxo2[8];
    // signal input signature1[768]; 
    // signal input signature2[768];
    signal input hash[256];
    signal output chash;

    // Calculate the total number of inputs
    var total = 8+8;

    // Declare Poseidon component with the correct total number of inputs
    component poseidon = Poseidon(total);

    // Concatenate all input signals into a single array
    signal input_concat[total];

    for(var i=0;i<8;i++){
        input_concat[i] <== input_utxo1[i];
    }
    for(var i=0;i<8;i++){
        input_concat[8+i] <== input_utxo2[i];
    }
    // for(var i=0;i<8;i++){
    //     input_concat[16+i] <== output_utxo1[i];
    // }
    // for(var i=0;i<8;i++){
    //     input_concat[24+i] <== output_utxo2[i];
    // }

    // for (var i = 0; i < 768; i++) {
    //     input_concat[ 32 + i] <== signature1[i];
    // }

    // for (var i = 0; i < 768; i++) {
    //     input_concat[800 + i] <== signature2[i];
    // }

    // Assign inputs to the Poseidon component
    for (var i = 0; i < total; i++) {
        poseidon.inputs[i] <== input_concat[i];
    }

    // Connect Poseidon output to output signal
    chash <== poseidon.out;

    // Assert the output matches the public input hash
    // assert(out == public_input_hash);
}

component main { public [hash] } = hasher();
