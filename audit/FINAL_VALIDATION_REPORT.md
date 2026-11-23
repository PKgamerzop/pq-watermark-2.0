# Final validation report

Validated on 23 November 2026. The review started from [`a721bb6` on `paper-audit-fixes`](https://github.com/PKgamerzop/pq-watermark-2.0/commit/a721bb6b4aa1b0fc4d97c96b50c465e5fd1c8d63) in `PKgamerzop/pq-watermark-2.0`. The saved experimental evidence remains pinned to [`fc526ae`](https://github.com/PKgamerzop/pq-watermark-2.0/tree/fc526ae62ad030c07e51b57e6406acd837154ea3). Reviewed the original research audit, claim matrix, fixes changelog, and remaining issues alongside the current manuscript and repository artifacts.

**Result.** The revised manuscript passed the tested build, reference-resolution and saved-evidence checks. Editorial readiness depends on the selected venue. The historical alignment on/off replay remains blocked by the missing research watermark key.

## Completed review and corrections

- **References.** Checked 17 records and their manuscript uses. Corrected two IEEE proceedings page ranges, the IEEE-published spelling of the deepfake title, the Frontiers author names, the ACM proceedings title, and the USENIX and CIFAR-10 reference details. Preserved all 17 keys. [Reference verification](REFERENCE_VERIFICATION.md).
- **Related work and context.** Limited the Shor-era statement to RSA and discrete-logarithm-based signatures. The federated-learning comparison names the observed timing metric. The patent discussion treats the trusted execution environment as embodiment-specific. The deepfake study reports classifier metrics. The literature table names the evaluation focus consistently across classifier, media and assurance studies. The manuscript presents an integration and evaluation contribution. It makes no priority or across-system superiority claim.
- **Method and mathematics.** The Cover count concerns strict signs, fixed rows and order, and independent uniform labels. Both computed bounds and the immediately preceding residual cutoffs were checked with integer binomial sums. Two separately stated ideal nulls do not give a full-verifier false-accept probability. Reed–Solomon error/erasure correction remains within its stated distance condition. The original Merkle reference is historical, and the manuscript identifies the SHA-256 serialization as the project's format. Kuhn is historical context for the assignment problem. The repository calls SciPy's `linear_sum_assignment`.
- **Numbers and provenance.** Reconciled 756 marked and 54 attacked baseline CSV rows with their saved JSONs, verified 13 marked clean runs and matching baseline summaries, and reproduced the Phase 7 report in scratch. The 724 extraction controls, 189 structural outcomes with retries available, all three overwrite pairs, 3-bit recovery without erasures, 2-bit rejected-copy accuracy, and 36 common baseline configurations reconciled. The review used the saved training and accuracy results.
- **README and documentation.** The README now distinguishes exact outcomes with retries available from an assertion that each case was aligned. Its verifier instructions require independently trusted key material and a pinned or trusted profile. The restricted-loading and full-length statements account for the legacy branches. The current threat model and Phase 7 report match the narrowed manuscript claims. Historical reports, archived figures and earlier audit locators are provenance records.

## Test and replay results

Commands below run from the branch checkout. The CPU Python environment used Python 3.12.14, PyTorch 2.15.0+cpu, SciPy 1.17.0, reedsolo 1.7.0, and pytest 9.2.0. Installed CMake 3.31.10 and liboqs-python 0.16.0.2 in scratch. Built Open Quantum Safe liboqs tag 0.16.0 as a shared library using `-DOQS_BUILD_ONLY_LIB=ON -DBUILD_SHARED_LIBS=ON -DOQS_MINIMAL_BUILD=SIG_ml_dsa_65`.

```sh
validation="$PWD/.git/final-validation"
export PYTHONPATH="$validation/deps:/workspace/work/deps:$PWD"
export OQS_INSTALL_PATH="$validation/oqs-prefix"
export LD_LIBRARY_PATH="$validation/oqs-prefix/lib"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export MPLCONFIGDIR="$validation/mpl" XDG_CACHE_HOME="$validation/cache"

python -m pytest -p no:cacheprovider -q -rs \
  --ignore=tests/test_torch.py --ignore=tests/test_mldsa.py
python tests/test_mldsa.py
python -m verify.verify_release --release-dir release --public-key release/public_key.bin
```

| Check | Observed result |
|---|---|
| pytest suite | **86 passed, 0 failed, 0 skipped** in 11.45 s. The two import-time smoke programs were excluded from collection and handled separately. The formerly skipped Phase 2 signature test and Phase 5/6b tests ran with liboqs. |
| `python tests/test_mldsa.py` | **Passed**, exit 0. ML-DSA-65 was enabled, key/signature lengths were 1,952/3,309 bytes, the intended message verified, and the tampered message failed verification. The test uses temporary signing material. |
| `python -m verify.verify_release --release-dir release --public-key release/public_key.bin` | **Passed**, exit 0. All five release checks passed, including signature and payload consistency. This validates the repository's pinned key and signed record. |
| CIFAR-10 smoke program and dataset commitment | **Passed on the completed archive.** The initial standalone download was interrupted after the alternate attempt passed (exit 130). The first ranged download returned HTTP 503 for some parts. A lower-concurrency retry completed the official archive and matched torchvision’s MD5. The smoke program then loaded 50,000 training images with shape 3 × 32 × 32 and exited 0. The release verifier independently recomputed the dataset Merkle root, matched it with the signed manifest, and exited 0. |
| Phase 7 report and reconciliation | **Passed.** Ran `python -m experiments.phase7.robustness_report --plots "$validation/report/plots" --out "$validation/report/phase7_results.md"` and `python "$validation/reconcile.py"`. The scratch reconciliation checked the JSON/CSV outcomes, counts, thresholds, tails one count below each cutoff, sign tie rule, and independently checked the release with `cryptography`. The regenerated control summary matched byte for byte. The baseline comparison rows agreed within `1e-12` for floating drops with identical categorical outcomes and displayed rates. |
| Matched alignment on/off replay | **Blocked at preflight** (exit 2). The existing `runs/attacks/wm/seed0/permute_all/rep0/model.pt` checkpoint and release public key were present and liboqs worked. `keys/watermark_key.bin` was absent. No historical verifier verdict was generated, and no substitute key was generated or used for the historical evaluation. |

The standalone CIFAR-10 and dataset-commitment commands, after placing the verified official archive under scratch `data/`:

```sh
repo="$PWD"
(cd "$validation/cifar/prepared" && python "$repo/tests/test_torch.py")
python -m verify.verify_release --release-dir release --public-key release/public_key.bin \
  --check-dataset --cifar-root "$validation/cifar/prepared/data"
```

The matched-replay preflight verified the required inputs before invoking the model verifier:

```sh
python - <<'PY'
from pathlib import Path
p = Path('runs/attacks/wm/seed0/permute_all/rep0/model.pt')
assert p.is_file() and Path('release/public_key.bin').is_file()
key = Path('keys/watermark_key.bin')
print(f'Matched-replay input preflight: checkpoint={p.is_file()}, research_watermark_key={key.is_file()}')
if not key.is_file():
    raise SystemExit(2)
PY
```

With authorized access to the matching key, the planned comparison uses the same checkpoint, release inputs and extraction settings (`--ecc rs32 --n-bits 256 --layer features.6.0.weight --mode mean`) and changes only `--no-align`. Synthetic alignment tests that passed under pytest provide implementation checks. They do not reproduce the historical experiment.

## IEEEtran build and layout

Built a scratch copy with the IEEEtran class and style using, in order, `pdflatex -interaction=nonstopmode -halt-on-error main.tex`, `bibtex main`, and the same pdfLaTeX command twice. The final letter-size PDF has eight pages. Checked the PDF captions and LaTeX auxiliary labels for eight figures, five numbered tables, five named equations and 17 bibliography entries. The final logs have no undefined references, undefined citations, or overfull boxes. Two underfull vertical-box messages remain. The related-work table now uses ragged-right text for its narrow cells. `pdffonts` reported all fonts embedded and `pdfimages -list` showed each figure exceeding 300 pixels per inch at placement size.

Reviewed rendered pages at normal page size and with zoom. Figure panels, symbols and axes are distinguishable. The seed legends in the smaller single-column plots and the count labels in Figure 8A are dense at page scale. The last page has uneven column fill. These are layout issues for venue-specific editing. The manuscript retains IEEE conference mode and its author block. [Submission blockers](SUBMISSION_BLOCKERS.md).
