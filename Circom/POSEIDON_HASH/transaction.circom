pragma circom 2.0.0;
include "./circomlib/circuits/poseidon.circom";

template hasher(){

    signal input utxo_id;
    signal input amount;
    signal input output_address;
    signal input signature;
    signal input public_input_hash; // Public input representing the hash of private inputs
    signal output out;

    // Declare Poseidon component
    component poseidon = Poseidon(4);
    
    // Connect private inputs to Poseidon component
    poseidon.inputs[0] <== utxo_id;
    poseidon.inputs[1] <== amount;
    poseidon.inputs[2] <== output_address;
    poseidon.inputs[3] <== signature;
    
    // Connect Poseidon output to output signal
    out <== poseidon.out;

    // assert(out==public_input_hash);

}
component main{public[public_input_hash]} = hasher();

