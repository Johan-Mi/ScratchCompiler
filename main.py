#!/usr/bin/env python3
"""This module compiles code to scratch projects."""

import os
import json
import shutil
from hashlib import md5
from lark import Lark

from transformer import GrammarTransformer
from optimize import optimize
from scratchify import scratchify


def main():
    """Compiles program.scratch to a scratch project."""
    with open("grammar.lark") as grammar_file:
        grammar = grammar_file.read()
    parser = Lark(grammar, parser="lalr", transformer=GrammarTransformer)

    with open("program.scratch") as source_file:
        source_code = source_file.read()
    parsed = parser.parse(source_code)
    parsed = optimize(parsed)
    parsed = scratchify(parsed)

    backdrop_md5 = md5sum("resources/backdrop.svg")

    for i in parsed["targets"]:
        i["costumes"] = [{
            "assetId": backdrop_md5,
            "name": "backdrop",
            "md5ext": f"{backdrop_md5}.svg",
            "dataFormat": "svg",
            "rotationCenterX": 240,
            "rotationCenterY": 180
        }]

    try:
        with open("parsed.json", "w") as parsed_json_file:
            json.dump(parsed, parsed_json_file, indent="\t")
    except ValueError:
        print(parsed)

    create_project_files(parsed)


def md5sum(file_name):
    """Returns the md5 hash of a file."""
    with open(file_name, "rb") as file:
        return md5(file.read()).hexdigest()


def create_project_files(project):
    """Creates a scratch project file."""
    try:
        shutil.rmtree("project")
    except FileNotFoundError:
        pass
    os.mkdir("project")

    with open("project/project.json", "w") as project_json_file:
        json.dump(project, project_json_file)

    shutil.copy(
        "resources/backdrop.svg",
        "project/%s.svg" % project["targets"][0]["costumes"][0]["assetId"])

    os.system("zip --quiet -r project.sb3 project")
    shutil.rmtree("project")


if __name__ == "__main__":
    main()
