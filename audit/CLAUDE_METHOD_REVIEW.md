# Methodology integration review

Compared the uploaded section with `paper1/method.tex` at `38de156` on `paper-audit-fixes`. Reviewed the final validation report, research audit and claim evidence matrix. Checked the edited claims against the implementation. The input's editorial comments were treated as review annotations.

## Accepted and modified edits

| Marker | Resolution |
|---|---|
| F1 | Confirmed one watermark objective per run. `embedding/projection.py` selects BCE with logits or hinge with ReLU, and `training/train_watermarked.py` adds the selected loss weighted by λ. Defined λ and the hinge margin in the method and pointed to the evaluation for λ = 20 and m = 1.5. |
| F2 | Made the direction explicit. Compensated input permutations reorder the carrier blocks. Multiplying the upstream activation by α and dividing the receiving convolution weights by α maps the corresponding carrier block to its original value divided by α. This matches `attacks/weight_attacks.py`. The function preservation applies in exact arithmetic to the studied model. |
| F3 | Retained “heuristic eligibility rule” for applying the Cover calculation to the retry gate. The count bounds strict fixed-order fits under independent uniform labels. It gives no bound for target-dependent assignment followed by Reed–Solomon decoding. `embedding/align.py` can pass a successful LP result to the decoder even if its margin is nonpositive. |
| F4 | Rewrote the opening of Residual Agreement to require failure of exact recovery on the raw extraction and all permitted retries. The residual statistic uses only the original-order logits. Ordinary decode failure and a same-length digest mismatch can reach this check. Extraction exceptions and unexpected decoded lengths bypass it. See `verify/verify_model.py:128–189`. |
| F5 | Defined the leaf index, label and pixel symbols before their equation and specified height-width-channel byte order. Defined permutation direction as destination block c selecting source block π(c), matching `embedding/align.py`. |

Accepted the clearer trust assumptions, manifest serialization, carrier description and verdict wording. Omitted the opening roadmap paragraph. Kept the Reed–Solomon correction statement conditional on the error and erasure counts, and specified the actual hard-bit mapping. Updated the figure caption to require a digest match rather than decoder success alone. Removed all editorial markers. Equation bodies, labels, citation order, figure inclusion and numerical results match the validated base.

## Factual checks

`crypto/dataset.py`, `crypto/merkle.py`, `crypto/manifest.py` and `crypto/signing.py` support the leaf encoding, odd-node promotion, JSON encoding, key identifier and manifest digest. `embedding/keys.py`, `embedding/projection.py` and `embedding/ecc.py` support the keyed projection, loss equations, parity lengths and erasure schedule. The ML-DSA-65 sizes and Cover and binomial calculations retain the values checked in the final validation report.

Each candidate first tries hard RS decoding and, after decoder failure, the configured confidence-ranked erasure schedule. The first successful decoder return ends that candidate's internal schedule. A wrong digest can still trigger a retry. The eligible candidates are the nonidentity assignment, a successful original-order scale fit, and a successful scale fit after a nonidentity normalized-block assignment. A full digest match takes precedence over residual evidence. The RS32 and RS16 residual thresholds retain their stated one-shot null assumptions.

## Compilation and tests

Built the complete IEEEtran manuscript with pdfLaTeX, BibTeX, then two further pdfLaTeX passes using `-interaction=nonstopmode -halt-on-error`. The final PDF has eight pages, all 17 citations, eight figure labels, five table labels and five named equations. The final log had no compilation errors, undefined citations or references, or overfull boxes. It reported one underfull vertical box.

With the existing liboqs-enabled validation environment, ran `python -m pytest -p no:cacheprovider -q tests/test_phase4.py tests/test_phase6b.py tests/test_hinge_loss.py`. **27 passed, 0 failed, 0 skipped.**

## Remaining author decisions

Select the IEEE venue and check its page limit, author disclosure and artifact rules. If the chosen track requires a matched historical alignment replay, arrange controlled access to the corresponding research watermark key. The recorded results do not establish a false-accept bound for the complete verifier.
