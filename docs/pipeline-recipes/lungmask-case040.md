# Lungmask Recipe case040

## Goal
Generate aligned mask slices for case040 with deterministic naming.

## Commands
```bash
cd ~/git/lungmask
lungmask data/case040.nii.gz workspace/masks/case040-mask.nii.gz \
  --modelname R231 \
  --export-png-dir workspace/masks/case040 \
  --png-prefix case040 \
  --axis x \
  --index-width 3 \
  --manifest-json workspace/masks/case040-manifest.json \
  --skip-volume-output
```

## Integration Notes
- Match `--png-prefix`, `--axis`, and `--index-width` with converter output.
- Feed `workspace/images/case040` and `workspace/masks/case040` into pair indexing.
