pragma circom 2.0.0;
// See ../Makefile for make instructions
//
//
// Note: we need to be careful of the conversions
// between ints and bytes and bit arrays
// 
// Two problems to be careful of:
// - SHA256 is sensitive to the number of bits of
//   of input. So extra 0 bits are not ignored
// - It is too easy to reverse the order of 
//   bytes or bits in bytes or bits in instructions
// - input.json: specify the integers as json strings
//   regular integers are restricted to 2^53
//   but strings get converted to int/field
// 
// Num2Bits: out[0] is least-significant-bit of in
// Bits2Num: in[0] becomes least-significant-bit of out
// 
// Note: this just computes the hash
// You can see the output hash value in verifier/sha256_public.json
// It doesn't actually verify anything
// To do that you'd have to make the hash an input

include "./circomlib/circuits/sha256/sha256.circom";
include "./circomlib/circuits/bitify.circom";

template SHA256Hasher(N) {
    // inputs and hash are arrays of bits
    signal input inputs[N];
    signal input hash[256];
    signal output chash[256];

    component sha256hasher = Sha256(N);
    for (var i = 0; i < N; i++) {
        sha256hasher.in[i] <== inputs[i];
    }

    // the final assertion
    for (var i = 0; i < 256; i++) {
        chash[i] <== sha256hasher.out[i];
        hash[i] === sha256hasher.out[i];
    }
}

component main {public [inputs, hash]} = SHA256Hasher(8);
