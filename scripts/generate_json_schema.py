"""Generates the json schema for top-level pydantic objects"""
import os
from pathlib import Path

import typer
from slugify import slugify

from pycasting.pydanticmodels.predictions import Scenario


def main(output_dir: Path = "generated/schema"):
    classes = [
        Scenario,
    ]

    os.makedirs(output_dir, exist_ok=True)

    with typer.progressbar(classes) as progress:
        for clazz in progress:
            typer.echo(f"Exporting {typer.style(clazz.__name__, fg=typer.colors.CYAN)}")
            with open(output_dir / f"{slugify(clazz.__name__)}.json", "w") as f:
                f.write(clazz.schema_json(indent=2))


if __name__ == "__main__":
    typer.run(main)
