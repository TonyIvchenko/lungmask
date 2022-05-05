# Lungmask Recipe case042

## Goal
Generate aligned mask slices for case042 with deterministic naming.

## Commands
```bash
cd ~/git/lungmask
lungmask data/case042.nii.gz workspace/masks/case042-mask.nii.gz \
  --modelname R231CovidWeb \
  --export-png-dir workspace/masks/case042 \
  --png-prefix case042 \
  --axis z \
  --index-width 3 \
  --manifest-json workspace/masks/case042-manifest.json \
  --skip-volume-output
```

## Integration Notes
- Match `--png-prefix`, `--axis`, and `--index-width` with converter output.
- Feed `workspace/images/case042` and `workspace/masks/case042` into pair indexing.
