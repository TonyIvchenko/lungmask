# Lungmask Recipe case037

## Goal
Generate aligned mask slices for case037 with deterministic naming.

## Commands
```bash
cd ~/git/lungmask
lungmask data/case037.nii.gz workspace/masks/case037-mask.nii.gz \
  --modelname R231 \
  --export-png-dir workspace/masks/case037 \
  --png-prefix case037 \
  --axis x \
  --index-width 3 \
  --manifest-json workspace/masks/case037-manifest.json \
  --skip-volume-output
```

## Integration Notes
- Match `--png-prefix`, `--axis`, and `--index-width` with converter output.
- Feed `workspace/images/case037` and `workspace/masks/case037` into pair indexing.
