# V3 schema-conditioned decision prototype

Minimal CAT/ORD experiment for the lymphoma eCRF project.

The prototype keeps the V2 150M encoder and 45k-character input, encodes the textual
field/value schema once, and scores every candidate with two cross-attention layers.
There are no span heads, DATE/NUM heads, or inter-field constraints.

Training modes:

- `ce`: cross-entropy only;
- `proper`: CE + Brier, plus RPS on ordinal fields;
- `rlcd`: CE anchor plus a group-relative, calibrated-decision policy objective.

`rlcd` is deliberately called RLCD-inspired: public descriptions do not provide enough
detail to claim a byte-for-byte reproduction of TypeSafe/Laya training.

The official train/validation/test split from
`rntc/lymphome-synth-v5-eval` is mandatory. Test evaluation is a separate command.

