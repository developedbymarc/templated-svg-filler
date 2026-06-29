# Templated SVG Filler

## Description

This simple python script takes a base SVG template and a JSON file to generate new SVGs with the information provided in the JSON file.

## Usage

### CLI

```
usage: svgfiller.py [-h] [-o OUTPUT] [-d OUTDIR] template_svg json_file

positional arguments:
  template_svg
  json_file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        base output filename (used as a prefix)
  -d OUTDIR, --outdir OUTDIR
                        output directory
```

### JSON Formatting

```json
[
    {
        "txt_el1_id": { "value": "LOREM IPSUM" }, 
        "txt_el2_id": { "value": "DOLOR SIT AMET", "type": "text" },
        "img_el1_id": { "value": "relative/path/to/image", "type": "image" }
    },
    ...
]
```

## Limitations

The program is currently limited to text and image insertion with no stylistic variation.
