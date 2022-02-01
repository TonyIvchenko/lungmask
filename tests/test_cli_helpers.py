import importlib.util
import sys
import types
from pathlib import Path

import numpy as np
import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "lungmask" / "__main__.py"


def load_cli_module(fake_writes):
    fake_mask_module = types.ModuleType("lungmask.mask")
    fake_mask_module.available_models = lambda _modeltype: ["R231"]

    fake_utils_module = types.ModuleType("lungmask.utils")
    fake_utils_module.get_input_image = lambda _path: None

    fake_package = types.ModuleType("lungmask")
    fake_package.mask = fake_mask_module
    fake_package.utils = fake_utils_module

    fake_sitk = types.ModuleType("SimpleITK")
    fake_sitk.GetImageFromArray = lambda array: np.asarray(array)
    fake_sitk.WriteImage = lambda image, path: fake_writes.append((np.asarray(image), str(path)))

    sys.modules["lungmask"] = fake_package
    sys.modules["lungmask.mask"] = fake_mask_module
    sys.modules["lungmask.utils"] = fake_utils_module
    sys.modules["SimpleITK"] = fake_sitk

    spec = importlib.util.spec_from_file_location("lungmask_cli_main", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build_slice_filename_matches_shared_convention():
    module = load_cli_module(fake_writes=[])
    assert module.build_slice_filename("case", 4) == "case_z004.png"
    assert module.build_slice_filename("case", 4, axis="x") == "case_x004.png"


def test_iter_mask_slices_supports_axis_selection():
    module = load_cli_module(fake_writes=[])
    volume = np.arange(2 * 3 * 4).reshape((2, 3, 4))
    slices = list(module.iter_mask_slices(volume, axis="y"))

    assert len(slices) == 3
    assert np.array_equal(slices[0][1], volume[:, 0, :])


def test_export_png_slices_writes_and_skips_existing(tmp_path):
    writes = []
    module = load_cli_module(fake_writes=writes)
    output_dir = tmp_path / "out"
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = output_dir / "scan_z001.png"
    existing.write_bytes(b"existing")

    records = module.export_png_slices(
        mask_array=np.zeros((1, 2, 2), dtype=np.uint8),
        output_dir=output_dir,
        base_name="scan",
        overwrite=False,
    )

    assert len(records) == 2
    assert records[0]["status"] == "skipped_existing"
    assert records[1]["status"] == "written"
    assert len(writes) == 1


def test_validate_cli_args_requires_any_output(tmp_path):
    module = load_cli_module(fake_writes=[])
    parser = module.build_parser("0.0.0")
    input_path = tmp_path / "input.nii.gz"
    input_path.write_text("stub", encoding="utf-8")
    args = parser.parse_args([str(input_path), "--skip-volume-output"])
    args.export_png_dir = None

    with pytest.raises(SystemExit):
        module.validate_cli_args(args, parser)
