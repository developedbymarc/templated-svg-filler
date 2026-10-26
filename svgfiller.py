#!/usr/bin/env python3

import argparse
import base64
import json
import mimetypes
import re
from pathlib import Path


def escape_xml(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def svg_data_url(image_path: str) -> str:
    path = Path(image_path)
    mime, _ = mimetypes.guess_type(path.name)
    if mime is None:
        mime = "application/octet-stream"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def replace_text(svg: str, field: str, value: str) -> str:
    pattern = rf'(<text[^>]*id="{re.escape(field)}"[^>]*>)(.*?)(</text>)'
    return re.sub(pattern, r"\1" + escape_xml(value) + r"\3", svg, flags=re.DOTALL)


def replace_image(svg: str, field: str, value: str) -> str:
    data_url = svg_data_url(value)

    # common SVG image formats: <image id="pfp" href="...">
    pattern_href = rf'(<image[^>]*id="{re.escape(field)}"[^>]*href=")([^"]*)(")'
    svg = re.sub(pattern_href, r"\1" + data_url + r"\3", svg, flags=re.DOTALL)

    # older SVG syntax: xlink:href
    pattern_xlink = rf'(<image[^>]*id="{re.escape(field)}"[^>]*xlink:href=")([^"]*)(")'
    svg = re.sub(pattern_xlink, r"\1" + data_url + r"\3", svg, flags=re.DOTALL)

    return svg


def apply_fields(svg: str, fields: dict) -> str:
    for field_id, spec in fields.items():
        value = spec.get("value", "")
        element_type = spec.get("type", "text")

        if element_type == "text":
            svg = replace_text(svg, field_id, value)
        elif element_type == "image":
            svg = replace_image(svg, field_id, value)
        else:
            raise ValueError(
                f"Unsupported element type: {element_type} for field {field_id}"
            )

    return svg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template_svg")
    parser.add_argument("json_file")
    parser.add_argument(
        "-o",
        "--output",
        default="output.svg",
        help="base output filename (used as a prefix)",
    )
    parser.add_argument("-d", "--outdir", default="out", help="output directory")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    template = Path(args.template_svg).read_text(encoding="utf-8")
    fields = json.loads(Path(args.json_file).read_text(encoding="utf-8"))

    output_path = Path(args.output)
    stem = output_path.stem
    suffix = output_path.suffix or ".svg"

    if isinstance(fields, list):
        for i, item in enumerate(fields):
            if not isinstance(item, dict):
                raise ValueError(
                    f"Expected list elements to be dicts, got {type(item)} at index {i}"
                )
            filled = apply_fields(template, item)
            out = outdir / f"{stem}_{i + 1}{suffix}"
            out.write_text(filled, encoding="utf-8")

    elif isinstance(fields, dict):
        filled = apply_fields(template, fields)
        out = outdir / f"{stem}{suffix}"
        out.write_text(filled, encoding="utf-8")

    else:
        raise ValueError(f"Expected JSON root to be dict or list, got {type(fields)}")


if __name__ == "__main__":
    main()
