# Lungmask Recipe case036

## Goal
Generate aligned mask slices for case036 with deterministic naming.

## Commands
```bash
cd ~/git/lungmask
lungmask data/case036.nii.gz workspace/masks/case036-mask.nii.gz \
  --modelname R231CovidWeb \
  --export-png-dir workspace/masks/case036 \
  --png-prefix case036 \
  --axis z \
  --index-width 3 \
  --manifest-json workspace/masks/case036-manifest.json \
  --skip-volume-output
```

## Integration Notes
- Match `--png-prefix`, `--axis`, and `--index-width` with converter output.
- Feed `workspace/images/case036` and `workspace/masks/case036` into pair indexing.
