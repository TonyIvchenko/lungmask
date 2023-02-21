from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "lungmask" / "export_helpers.py"
SPEC = spec_from_file_location("export_helpers", MODULE_PATH)
export_helpers = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(export_helpers)


def _sample_payload():
    return {
        "input": "scan.nii.gz",
        "output_volume": "scan-mask.nii.gz",
        "modeltype": "unet",
        "modelname": "R231",
        "export_png_dir": "masks",
        "png_prefix": "scan",
        "axis": "z",
        "index_width": 3,
        "png_records": [
            {"status": "written", "path": "masks/scan_z001.png", "slice_index": 1},
            {"status": "written", "path": "masks/scan_z002.png", "slice_index": 2},
            {"status": "skipped_existing", "path": "masks/scan_z002.png", "slice_index": 2},
        ],
    }


def test_export_model_name():
    assert export_helpers.export_model_name(_sample_payload()) == "R231"


def test_export_model_type():
    assert export_helpers.export_model_type(_sample_payload()) == "unet"


def test_export_output_volume():
    assert export_helpers.export_output_volume(_sample_payload()) == "scan-mask.nii.gz"


def test_export_png_dir():
    assert export_helpers.export_png_dir(_sample_payload()) == "masks"


def test_export_png_prefix():
    assert export_helpers.export_png_prefix(_sample_payload()) == "scan"


def test_export_axis():
    assert export_helpers.export_axis(_sample_payload()) == "z"
