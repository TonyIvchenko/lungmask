"""Helpers for inspecting lungmask export manifests."""


def _records(payload):
    return list(payload.get("png_records", []))


def export_model_name(payload):
    return payload.get("modelname")
