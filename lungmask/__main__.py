import sys
import argparse
import json
import logging
from pathlib import Path
from lungmask import mask
from lungmask import utils
from lungmask import export_helpers
import os
import SimpleITK as sitk
import numpy as np
from importlib.metadata import PackageNotFoundError, version

FUSED_MODEL_NAME = "LTRCLobes_R231"


def path(string):
    if os.path.exists(string):
        return string
    else:
        sys.exit(f'File not found: {string}')


def strip_nii_extension(path_value):
    filename = Path(path_value).name
    if filename.endswith(".nii.gz"):
        return filename[:-7]
    if filename.endswith(".nii"):
        return filename[:-4]
    return Path(path_value).stem


def build_slice_filename(base_name, slice_index, volume_index=None, index_width=3, axis="z"):
    if axis not in {"x", "y", "z"}:
        raise ValueError(f"Unsupported axis '{axis}'. Expected one of: x, y, z.")
    if volume_index is None:
        return f"{base_name}_{axis}{slice_index:0{index_width}d}.png"
    return (
        f"{base_name}_t{volume_index:0{index_width}d}_{axis}{slice_index:0{index_width}d}.png"
    )


def ensure_mask_volume(mask_array):
    if mask_array.ndim == 2:
        return mask_array[None, :, :]
    if mask_array.ndim == 3:
        return mask_array
    raise ValueError(f"Expected 2D/3D mask array, got shape {mask_array.shape}.")


def iter_mask_slices(mask_array, axis="z"):
    axis_to_index = {"x": 0, "y": 1, "z": 2}
    if axis not in axis_to_index:
        raise ValueError(f"Unsupported axis '{axis}'. Expected one of: x, y, z.")

    volume = ensure_mask_volume(mask_array)
    axis_index = axis_to_index[axis]
    total_slices = volume.shape[axis_index]

    for current_slice in range(total_slices):
        yield current_slice + 1, np.take(volume, current_slice, axis=axis_index)


def export_png_slices(
    mask_array,
    output_dir,
    base_name,
    axis="z",
    index_width=3,
    overwrite=False,
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for slice_index, slice_data in iter_mask_slices(mask_array, axis=axis):
        image_name = build_slice_filename(
            base_name=base_name,
            slice_index=slice_index,
            axis=axis,
            index_width=index_width,
        )
        image_path = output_dir / image_name
        if image_path.exists() and not overwrite:
            records.append({"slice_index": slice_index, "path": str(image_path), "status": "skipped_existing"})
            continue

        slice_image = sitk.GetImageFromArray(slice_data.astype(np.uint8))
        sitk.WriteImage(slice_image, str(image_path))
        records.append({"slice_index": slice_index, "path": str(image_path), "status": "written"})
    return records


def build_manifest(args, batchsize, png_records):
    return {
        "input": args.input,
        "output_volume": args.output,
        "modeltype": args.modeltype,
        "modelname": args.modelname,
        "cpu": args.cpu,
        "batchsize": batchsize,
        "workers": args.workers,
        "noHU": args.noHU,
        "export_png_dir": str(args.export_png_dir) if args.export_png_dir is not None else None,
        "png_prefix": args.png_prefix,
        "axis": args.axis,
        "index_width": args.index_width,
        "overwrite_png": args.overwrite_png,
        "png_records": png_records,
    }


def positive_int(value):
    ivalue = int(value)
    if ivalue < 1:
        raise argparse.ArgumentTypeError("batchsize must be >= 1")
    return ivalue


def run_inference(input_image, args, batchsize):
    if args.modelname == FUSED_MODEL_NAME:
        return mask.apply_fused(
            input_image,
            force_cpu=args.cpu,
            batch_size=batchsize,
            volume_postprocessing=not args.nopostprocess,
            noHU=args.noHU,
            dataloader_workers=args.workers,
        )

    model = mask.get_model(args.modeltype, args.modelname)
    return mask.apply(
        input_image,
        model,
        force_cpu=args.cpu,
        batch_size=batchsize,
        volume_postprocessing=not args.nopostprocess,
        noHU=args.noHU,
        dataloader_workers=args.workers,
    )


def normalize_nohu_output(result, output_path):
    file_ending = os.path.splitext(output_path)[1].lower().lstrip(".")
    if file_ending in {"jpg", "jpeg", "png"}:
        max_value = int(result.max())
        if max_value > 0:
            result = (result / max_value * 255).astype(np.uint8)
        else:
            result = np.zeros_like(result, dtype=np.uint8)
    if result.ndim == 3:
        result = result[0]
    return result


def copy_image_metadata(result_out, input_image):
    if result_out.GetDimension() == input_image.GetDimension():
        result_out.CopyInformation(input_image)


def configure_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def validate_cli_args(args, parser):
    if args.noHU and os.path.isdir(args.input):
        parser.error("--noHU expects an input file, not a directory")
    if args.index_width < 1:
        parser.error("--index-width must be >= 1")
    if args.skip_volume_output and args.output is None and args.export_png_dir is None:
        parser.error("nothing to save: provide output path and/or --export-png-dir")
    if not args.skip_volume_output and args.output is None:
        parser.error("output path is required unless --skip-volume-output is set")


def build_parser(package_version):
    model_choices = mask.available_models("unet") + [FUSED_MODEL_NAME]
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input', type=path, help='Path to the input image, can be a folder for dicoms')
    parser.add_argument('output', metavar='output', nargs='?', type=str, help='Filepath for output lungmask volume')
    parser.add_argument('--modeltype', help='Default: unet', type=str, choices=['unet'], default='unet')
    parser.add_argument('--modelname', help="Specifies the trained model. Default: R231", type=str, choices=model_choices, default='R231')
    parser.add_argument('--cpu', help="Force using the CPU even when a GPU is available, will override batchsize to 1", action='store_true')
    parser.add_argument('--nopostprocess', help="Deactivates postprocessing (removal of unconnected components and hole filling)", action='store_true')
    parser.add_argument('--noHU', help="For processing of images that are not encoded in hounsfield units (HU). E.g. png or jpg images from the web. Be aware, results may be substantially worse on these images", action='store_true')
    parser.add_argument('--batchsize', type=positive_int, help="Number of slices processed simultaneously. Lower number requires less memory but may be slower.", default=20)
    parser.add_argument('--workers', type=positive_int, help="Number of DataLoader worker processes.", default=1)
    parser.add_argument('--export-png-dir', type=Path, help="Optional output folder for per-slice PNG masks.")
    parser.add_argument('--png-prefix', type=str, help="Optional basename prefix for exported PNG masks.")
    parser.add_argument('--axis', type=str, choices=['x', 'y', 'z'], default='z', help="Axis suffix used in PNG filenames.")
    parser.add_argument('--index-width', type=int, default=3, help="Zero-padding width for PNG slice indices.")
    parser.add_argument('--overwrite-png', action='store_true', help="Overwrite existing PNG mask slices.")
    parser.add_argument('--skip-volume-output', action='store_true', help="Skip writing the output volume file.")
    parser.add_argument('--manifest-json', type=Path, help="Optional path for writing run/export metadata as JSON.")
    parser.add_argument('--verbose', help="Enable verbose logging output", action='store_true')
    parser.add_argument('--version', help="Shows the current version of lungmask", action='version', version=package_version)
    return parser


def main(argv=None):
    try:
        package_version = version("lungmask")
    except PackageNotFoundError:
        package_version = "0+unknown"

    parser = build_parser(package_version)
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    validate_cli_args(args, parser)
    configure_logging(args.verbose)
    
    batchsize = args.batchsize
    if args.cpu:
        batchsize = 1

    logging.info(f'Load model')
    
    input_image = utils.get_input_image(args.input)
    logging.info(f'Infer lungmask')
    result = run_inference(input_image, args, batchsize)
    png_records = []

    if args.export_png_dir is not None:
        png_base_name = args.png_prefix or strip_nii_extension(args.input)
        png_records = export_png_slices(
            mask_array=result,
            output_dir=args.export_png_dir,
            base_name=png_base_name,
            axis=args.axis,
            index_width=args.index_width,
            overwrite=args.overwrite_png,
        )
        summary = export_helpers.export_summary({"png_records": png_records})
        logging.info(
            "Exported PNG masks to %s (%s written, %s skipped)",
            args.export_png_dir,
            summary["written"],
            summary["skipped_existing"],
        )
        
    if not args.skip_volume_output:
        if args.noHU:
            result_to_save = normalize_nohu_output(result, args.output)
        else:
            result_to_save = result

        result_out = sitk.GetImageFromArray(result_to_save)
        copy_image_metadata(result_out, input_image)
        logging.info(f'Save result to: {args.output}')
        sitk.WriteImage(result_out, args.output)
    else:
        logging.info('Skipping volume output file due to --skip-volume-output')

    if args.manifest_json is not None:
        args.manifest_json.parent.mkdir(parents=True, exist_ok=True)
        payload = build_manifest(args=args, batchsize=batchsize, png_records=png_records)
        args.manifest_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logging.info('Saved manifest to: %s', args.manifest_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
