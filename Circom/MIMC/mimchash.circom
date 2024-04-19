pragma circom 2.0.0;

include "./circomlib/circuits/mimc.circom";

template hasher() {
    signal input input_utxo1;
    signal input input_utxo2;
    signal input output_utxo1;
    signal input output_utxo2;
    signal input signature1; 
    signal input signature2;
    signal input k; 
    signal output chash;

    // Declare MiMC7 component with the correct number of rounds
    component mimcHasher = MultiMiMC7(6,91);

    mimcHasher.in[0] <== input_utxo1;
    mimcHasher.in[1] <== input_utxo2;
    mimcHasher.in[2] <== output_utxo1;
    mimcHasher.in[3] <== output_utxo2;
    mimcHasher.in[4] <== signature1;
    mimcHasher.in[5] <== signature2;

    mimcHasher.k <== 91; // Connecting the k input

    // Connect MiMC7 output to output signal
    chash <== mimcHasher.out;
}

component main  = hasher();
