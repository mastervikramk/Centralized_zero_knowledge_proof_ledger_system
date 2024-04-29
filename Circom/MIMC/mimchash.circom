pragma circom 2.0.0;

include "./circomlib/circuits/mimc.circom";

template hasher() {
    var n=100;
    signal input utxo[n];

    signal output chash1;
    signal output chash2;
    signal output chash3;
    signal output chash4;
    signal output chash5;
    signal output chash6;
    signal output chash7;
    signal output chash8;
    signal output chash9;
    signal output chash10;

    signal input k;   
    component mimcHasher1 = MultiMiMC7(10,91);
    component mimcHasher2 = MultiMiMC7(10,91);
    component mimcHasher3 = MultiMiMC7(10,91);
    component mimcHasher4 = MultiMiMC7(10,91);
    component mimcHasher5 = MultiMiMC7(10,91);
    component mimcHasher6 = MultiMiMC7(10,91);
    component mimcHasher7 = MultiMiMC7(10,91);
    component mimcHasher8 = MultiMiMC7(10,91);
    component mimcHasher9 = MultiMiMC7(10,91);
    component mimcHasher10 = MultiMiMC7(10,91);

//   transaction 1
    for(var i=0;i<10;i++){
    mimcHasher1.in[i] <== utxo[i];}

    mimcHasher1.k <== 91;
    chash1 <== mimcHasher1.out;

//  transaction 2
    for(var i=10;i<20;i++){
    mimcHasher2.in[i-10] <== utxo[i];}

    mimcHasher2.k <== 91;
    chash2 <== mimcHasher1.out;

//  transaction 3
    for(var i=20;i<30;i++){
    mimcHasher3.in[i-20] <== utxo[i];}

    mimcHasher3.k <== 91;
    chash3 <== mimcHasher3.out;

//  transaction 4
    for(var i=30;i<40;i++){
    mimcHasher4.in[i-30] <== utxo[i];}

    mimcHasher4.k <== 91;
    chash4 <== mimcHasher4.out;

//  transaction 5
    for(var i=40;i<50;i++){
    mimcHasher5.in[i-40] <== utxo[i];}

    mimcHasher5.k <== 91;
    chash5 <== mimcHasher5.out;

//   transaction 6
    for(var i=50;i<60;i++){
    mimcHasher6.in[i-50] <== utxo[i];}

    mimcHasher6.k <== 91;
    chash6 <== mimcHasher6.out;

//  transaction 7
    for(var i=60;i<70;i++){
    mimcHasher7.in[i-60] <== utxo[i];}

    mimcHasher7.k <== 91;
    chash7 <== mimcHasher7.out;

//  transaction 8
    for(var i=70;i<80;i++){
    mimcHasher8.in[i-70] <== utxo[i];}

    mimcHasher8.k <== 91;
    chash8 <== mimcHasher8.out;

//  transaction 9
    for(var i=80;i<90;i++){
    mimcHasher9.in[i-80] <== utxo[i];}

    mimcHasher9.k <== 91;
    chash9 <== mimcHasher9.out;

//  transaction 10
    for(var i=90;i<100;i++){
    mimcHasher10.in[i-90] <== utxo[i];}

    mimcHasher10.k <== 91;
    chash10 <== mimcHasher10.out;

}

component main  = hasher();
