pragma circom 2.1.6;

// Proves privately that secret_value >= public_floor in an 8-bit bounded domain.
// The secret value is never an output. The public floor is the only public input.
template PrivateLowerBound() {
    signal input secret_value;
    signal input public_floor;
    signal input delta_bits[8];

    var i;
    signal delta;
    delta <== delta_bits[0] + 2*delta_bits[1] + 4*delta_bits[2] + 8*delta_bits[3]
        + 16*delta_bits[4] + 32*delta_bits[5] + 64*delta_bits[6] + 128*delta_bits[7];
    for (i = 0; i < 8; i++) {
        delta_bits[i] * (delta_bits[i] - 1) === 0;
    }
    secret_value === public_floor + delta;
}

component main {public [public_floor]} = PrivateLowerBound();
