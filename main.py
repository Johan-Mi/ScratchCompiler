#!/usr/bin/env python3

import os
import json
import shutil
from hashlib import md5
from lark import Lark

from transformer import GrammarTransformer
from optimize import optimize
from scratchify import scratchify

def main():
	with open("grammar.lark") as f:
		grammar = f.read()
	parser = Lark(grammar, parser="lalr", transformer=GrammarTransformer)

	with open("program.scratch") as f:
		sourceCode = f.read()
	parsed = parser.parse(sourceCode)
	parsed = optimize(parsed)
	parsed = scratchify(parsed)

	backdropMd5 = md5sum("resources/backdrop.svg")

	for i in parsed["targets"]:
		i["costumes"] = [{
			"assetId": backdropMd5,
			"name": "backdrop",
			"md5ext": f"{backdropMd5}.svg",
			"dataFormat": "svg",
			"rotationCenterX": 240,
			"rotationCenterY": 180}]

	try:
		with open("parsed.json", "w") as f:
			json.dump(parsed, f, indent="\t")
	except ValueError:
		print(parsed)

	createProjectFiles(parsed)

	# listMonitors = [
	# 	{
	# 		"listName": "console",
	# 		"width": 480,
	# 		"height": 360,
	# 		"x": 0,
	# 		"y": 0,
	# 	}
	# ]

	# varMonitors = [
	# 	# {
	# 		# "varName": "",
	# 		# "mode": "large",
	# 		# "x": 0,
	# 		# "y": 0,
	# 	# }
	# ]

	# monitors = [
	# 	{
	# 		"id": "monitor_%s" % mon["listName"],
	# 		"mode": "list",
	# 		"opcode": "data_listcontents",
	# 		"params": {
	# 			"LIST": mon["listName"],
	# 		},
	# 		"spriteName": None,
	# 		"value": "",
	# 		"width": mon["width"],
	# 		"height": mon["height"],
	# 		"x": mon["x"],
	# 		"y": mon["y"],
	# 		"visible": True,
	# 	} for mon in listMonitors] + [
	# 	{
	# 		"id": "monitor_%s" % mon["varName"],
	# 		"mode": mon["mode"],
	# 		"opcode": "data_variable",
	# 		"params": {
	# 			"VARIABLE": mon["varName"],
	# 		},
	# 		"spriteName": None,
	# 		"value": "",
	# 		"width": 0,
	# 		"height": 0,
	# 		"x": mon["x"],
	# 		"y": mon["y"],
	# 		"visible": True,
	# 	} for mon in varMonitors]

def md5sum(filename):
	with open(filename, "rb") as f:
		return md5(f.read()).hexdigest()

def createProjectFiles(project):
	try:
		shutil.rmtree("project")
	except FileNotFoundError:
		pass
	os.mkdir("project")

	with open("project/project.json", "w") as f:
		json.dump(project, f)

	shutil.copy("resources/backdrop.svg",
			"project/%s.svg" % project["targets"][0]["costumes"][0]["assetId"])

	os.system("zip --quiet -r project.sb3 project")
	shutil.rmtree("project")

if __name__ == "__main__":
	main()
