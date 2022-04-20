# Lungmask Recipe case038

## Goal
Generate aligned mask slices for case038 with deterministic naming.

## Commands
```bash
cd ~/git/lungmask
lungmask data/case038.nii.gz workspace/masks/case038-mask.nii.gz \
  --modelname LTRCLobes \
  --export-png-dir workspace/masks/case038 \
  --png-prefix case038 \
  --axis y \
  --index-width 3 \
  --manifest-json workspace/masks/case038-manifest.json \
  --skip-volume-output
```

## Integration Notes
- Match `--png-prefix`, `--axis`, and `--index-width` with converter output.
- Feed `workspace/images/case038` and `workspace/masks/case038` into pair indexing.
