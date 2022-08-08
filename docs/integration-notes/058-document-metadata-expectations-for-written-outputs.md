# Document metadata expectations for written outputs

## Why this matters
Mask export should mirror converter naming so pairing and split generation are straightforward.

## Quick command
```bash
cd ~/git/lungmask
lungmask data/sample.nii.gz workspace/sample-mask.nii.gz \
  --modelname R231 \
  --export-png-dir workspace/masks \
  --png-prefix sample \
  --axis z \
  --index-width 3 \
  --manifest-json workspace/masks/manifest.json \
  --skip-volume-output
```

## What to check
- Prefix/axis/index width match converter output.
- Manifest records match files in the mask folder.
