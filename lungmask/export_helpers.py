"""Helpers for inspecting lungmask export manifests."""


def _records(payload):
    return list(payload.get("png_records", []))


def export_model_name(payload):
    return payload.get("modelname")


def export_model_type(payload):
    return payload.get("modeltype")


def export_output_volume(payload):
    return payload.get("output_volume")


def export_png_dir(payload):
    return payload.get("export_png_dir")


def export_png_prefix(payload):
    return payload.get("png_prefix")


def export_axis(payload):
    return payload.get("axis")


def export_index_width(payload):
    return payload.get("index_width")


def export_records(payload):
    return _records(payload)
