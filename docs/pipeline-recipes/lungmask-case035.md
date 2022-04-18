# Lungmask Recipe case035

## Goal
Generate aligned mask slices for case035 with deterministic naming.

## Commands
```bash
cd ~/git/lungmask
lungmask data/case035.nii.gz workspace/masks/case035-mask.nii.gz \
  --modelname LTRCLobes \
  --export-png-dir workspace/masks/case035 \
  --png-prefix case035 \
  --axis y \
  --index-width 3 \
  --manifest-json workspace/masks/case035-manifest.json \
  --skip-volume-output
```

## Integration Notes
- Match `--png-prefix`, `--axis`, and `--index-width` with converter output.
- Feed `workspace/images/case035` and `workspace/masks/case035` into pair indexing.
