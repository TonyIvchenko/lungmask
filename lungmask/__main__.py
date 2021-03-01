import sys
import argparse
import logging
from lungmask import mask
from lungmask import utils
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
        )

    model = mask.get_model(args.modeltype, args.modelname)
    return mask.apply(
        input_image,
        model,
        force_cpu=args.cpu,
        batch_size=batchsize,
        volume_postprocessing=not args.nopostprocess,
        noHU=args.noHU,
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


def build_parser(package_version):
    model_choices = mask.available_models("unet") + [FUSED_MODEL_NAME]
    parser = argparse.ArgumentParser()
    parser.add_argument('input', metavar='input', type=path, help='Path to the input image, can be a folder for dicoms')
    parser.add_argument('output', metavar='output', type=str, help='Filepath for output lungmask')
    parser.add_argument('--modeltype', help='Default: unet', type=str, choices=['unet'], default='unet')
    parser.add_argument('--modelname', help="Specifies the trained model. Default: R231", type=str, choices=model_choices, default='R231')
    parser.add_argument('--cpu', help="Force using the CPU even when a GPU is available, will override batchsize to 1", action='store_true')
    parser.add_argument('--nopostprocess', help="Deactivates postprocessing (removal of unconnected components and hole filling)", action='store_true')
    parser.add_argument('--noHU', help="For processing of images that are not encoded in hounsfield units (HU). E.g. png or jpg images from the web. Be aware, results may be substantially worse on these images", action='store_true')
    parser.add_argument('--batchsize', type=positive_int, help="Number of slices processed simultaneously. Lower number requires less memory but may be slower.", default=20)
    parser.add_argument('--version', help="Shows the current version of lungmask", action='version', version=package_version)
    return parser


def main(argv=None):
    try:
        package_version = version("lungmask")
    except PackageNotFoundError:
        package_version = "0+unknown"

    parser = build_parser(package_version)
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    
    batchsize = args.batchsize
    if args.cpu:
        batchsize = 1

    logging.info(f'Load model')
    
    input_image = utils.get_input_image(args.input)
    logging.info(f'Infer lungmask')
    result = run_inference(input_image, args, batchsize)
        
    if args.noHU:
        result = normalize_nohu_output(result, args.output)
             
    result_out= sitk.GetImageFromArray(result)
    result_out.CopyInformation(input_image)
    logging.info(f'Save result to: {args.output}')
    sys.exit(sitk.WriteImage(result_out, args.output))


if __name__ == "__main__":
    main()
