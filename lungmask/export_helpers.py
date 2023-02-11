"""Helpers for inspecting lungmask export manifests."""


def _records(payload):
    return list(payload.get("png_records", []))


def export_model_name(payload):
    return payload.get("modelname")


def export_model_type(payload):
    return payload.get("modeltype")


def export_output_volume(payload):
    return payload.get("output_volume")
