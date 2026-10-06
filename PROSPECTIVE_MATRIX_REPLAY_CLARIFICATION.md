# Prospective 24-target matrix replay clarification

## Result

The original 24 prospective processing-time matrices are byte-exactly recoverable from
the prespecified seeds. All 24 regenerated CSV files match the archived SHA-256 fingerprints,
and all 24 reproduce the archived deterministic NEH normalization values.

## Recovered implementation detail

The prespecified protocol recorded NumPy `PCG64DXSM`, iid discrete Uniform{1,...,99},
and the seed formula `2026082701 + n*1000 + m`, but the archived text did not state the
integer `dtype` used in the original draw call. The archived fingerprints are reproduced by
a 16-bit integer draw stream:

`np.random.Generator(np.random.PCG64DXSM(seed)).integers(1, 100, size=(n,m), dtype=np.int16)`

For the range 1..99, `dtype=np.uint16` yields the same value stream and therefore the same
CSV bytes. The retained evidence identifies the 16-bit draw path but cannot distinguish
signed from unsigned 16-bit storage. An earlier replay attempt using NumPy's default
integer dtype (`int64`) produced 0/24 fingerprint matches because it follows a different
random-number-consumption path.

## NEH replay detail

The archived NEH values are reproduced by the deterministic NEH implementation used
by the supplied verifier: jobs are sorted by descending total processing time with job index
breaking sorting ties; jobs are then inserted sequentially at the best position, with the
earliest insertion position breaking equal-makespan insertion ties. With that rule, NEH
matches are 24/24.

## Scientific consequence

This is a reproducibility clarification, not a change to the prospective design, target panel,
action labels, GA outcomes, or endpoints. The reconstructed matrices are byte-identical to
the archived identities, so analyses requiring the exact prospective panel can be executed
without substituting new problem instances.
