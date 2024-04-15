pragma circom 2.0.0;

include "./circomlib/circuits/poseidon.circom";

template hasher() {
    signal input input_utxo1;
    signal input input_utxo2;
    signal input output_utxo1;
    signal input output_utxo2;
    signal input signature1; 
    signal input signature2;
    signal output chash;

   
    // Declare Poseidon component with the correct total number of inputs
    component poseidon = Poseidon(6);

    //passing inputs to the poseidon hash
    poseidon.inputs[0] <== input_utxo1;
    poseidon.inputs[1] <== input_utxo2;
    poseidon.inputs[2] <== output_utxo1;
    poseidon.inputs[3] <== output_utxo2;
    poseidon.inputs[4] <== signature1;
    poseidon.inputs[5] <== signature2;

    // Connect Poseidon output to output signal
    chash <== poseidon.out;

}
component main  = hasher();
