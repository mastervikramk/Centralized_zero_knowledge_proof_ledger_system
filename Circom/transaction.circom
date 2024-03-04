pragma circom 2.0.0;
include "./circomlib/circuits/poseidon.circom";


template hasher(){
    
    signal input utxo_id;
    signal input amount;
    signal input wallet_id;
    signal input transaction_id;
    signal output out;

    component poseidon = Poseidon(4);
    poseidon.inputs[0] <== utxo_id;
    poseidon.inputs[1] <== amount;
    poseidon.inputs[2] <== wallet_id;
    poseidon.inputs[3] <== transaction_id;
    out <== poseidon.out;

}

component main=hasher();