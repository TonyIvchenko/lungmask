# Lungmask Recipe case041

## Goal
Generate aligned mask slices for case041 with deterministic naming.

## Commands
```bash
cd ~/git/lungmask
lungmask data/case041.nii.gz workspace/masks/case041-mask.nii.gz \
  --modelname LTRCLobes \
  --export-png-dir workspace/masks/case041 \
  --png-prefix case041 \
  --axis y \
  --index-width 3 \
  --manifest-json workspace/masks/case041-manifest.json \
  --skip-volume-output
```

## Integration Notes
- Match `--png-prefix`, `--axis`, and `--index-width` with converter output.
- Feed `workspace/images/case041` and `workspace/masks/case041` into pair indexing.
