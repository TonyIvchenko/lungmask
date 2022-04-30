# Lungmask Recipe case039

## Goal
Generate aligned mask slices for case039 with deterministic naming.

## Commands
```bash
cd ~/git/lungmask
lungmask data/case039.nii.gz workspace/masks/case039-mask.nii.gz \
  --modelname R231CovidWeb \
  --export-png-dir workspace/masks/case039 \
  --png-prefix case039 \
  --axis z \
  --index-width 3 \
  --manifest-json workspace/masks/case039-manifest.json \
  --skip-volume-output
```

## Integration Notes
- Match `--png-prefix`, `--axis`, and `--index-width` with converter output.
- Feed `workspace/images/case039` and `workspace/masks/case039` into pair indexing.
