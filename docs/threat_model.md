# Threat model

## Release record and checkpoint association

The developer signs a manifest containing a dataset commitment and embeds the
manifest digest as a keyed weight watermark. The trusted auditor independently
obtains the signing public key, protects the separate watermark key, and has
white-box access to the suspect checkpoint. The auditor pins the extraction
profile to the release, including the carrier layer, mean mode, full payload
length, ECC variant, and alignment policy. Adjacent run settings are unsigned.
Use explicit options or trusted settings and leave the legacy short-payload
override disabled.

A valid ML-DSA-65 signature authenticates the manifest under the trusted key.
Exact watermark recovery supplies evidence of association with that manifest.
The optional dataset check compares supplied data with the signed root. Actual
training inputs, data quality, legal ownership and priority require independent
evidence. The signer supplies the timestamp.

## Evaluated adversaries

- A remover has the model weights and applies specified modifications.
  The same-layer overwrite knows the carrier and uses a competing mark with
  another key. A successful removal requires rejection within five accuracy
  points of the clean parent. The suite does not evaluate an adaptive
  verifier-query adversary or exposure of the original watermark key.
- Selected forgery fixtures exercise wrong keys, altered records and unrelated
  weights. They are checks on the implementation.
- Dataset-tampering fixtures change data after commitment and compare the
  supplied data against the signed root.

## Extraction and evidence

The verifier tries assignment and positive-scale fitting when eligible, then
compares the decoded payload with the full manifest digest. The Cover count
applies to a fixed-order strict scale-sign fit under independent uniform labels.
It serves as a retry gate. A false-accept bound for the target-adaptive assignment
and decoder remains open.

DAMAGED uses only the raw, original-order score after exact recovery fails.
The cutoff is 358/512 for RS32 or 280/384 for RS16. Each has a binomial tail below
2^-64 under a prespecified comparison with independent equiprobable hard decisions.
A zero logit maps to zero. The tail describes the stated null, and DAMAGED reports
residual agreement. The sampled control cases and structural results are
summarized in [the manuscript](../paper1/evaluation.tex).

## Limits and key custody

The evidence concerns SmallCNN and CIFAR-10 under a shared release and key.
Distillation, cross-layer overwriting, substantially longer fine-tuning,
architecture-changing edits and compromised keys remain outside the study.
Development signing material was shared within the team. Use separately managed
release credentials for deployment. A trusted timestamp or transparency log and
an auditor delegation and revocation mechanism remain outside the implementation.
