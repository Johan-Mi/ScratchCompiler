#!/usr/bin/env python3

import os
import json
import shutil
from hashlib import md5
from enum import Enum
from lark import Lark

from transformer import GrammarTransformer
from optimize import optimize

with open("grammar.lark") as f:
	grammar = f.read()

parser = Lark(grammar, parser="lalr", transformer=GrammarTransformer)

def main():
	with open("program.scratch") as f:
		sourceCode = f.read()
	parsed = parser.parse(sourceCode)
	parsed = optimize(parsed)

	try:
		with open("parsed.json", "w") as f:
			json.dump(parsed, f, indent="\t")
	except TypeError:
		print(parsed)

	# backdropMd5 = md5sum("resources/backdrop.svg")

	# variables = {

	# }

	# lists = {
	# 	"console": [
	# 		"Line 1", "Line 2",
	# 		"Line 3",
	# 		"Line 4",
	# 	],
	# }

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

	# blocks = {
	# 	"block_1": {
	# 		"opcode": "event_whenflagclicked",
	# 		"next": None,
	# 		"parent": None,
	# 		"inputs": {},
	# 		"fields": {},
	# 		"shadow": False,
	# 		"topLevel": True,

	# 		"x": 0,
	# 		"y": 0,
	# 	},
	# }

	# stage = {
	# 	"isStage": True,
	# 	"name": "Stage",
	# 	"variables": { "var_%s" % name : [name, value]
	# 		for name, value in variables.items() },
	# 	"lists": { "var_%s" % name : [name, value]
	# 		for name, value in lists.items() },
	# 	"broadcasts": {},
	# 	"blocks": blocks,
	# 	"comments": {},
	# 	"currentCostume": 0,
	# 	"costumes": [
	# 		{
	# 			"assetId": backdropMd5,
	# 			"name": "backdrop",
	# 			"md5ext": "%s.svg" % backdropMd5,
	# 			"dataFormat": "svg",
	# 			"rotationCenterX": 240,
	# 			"rotationCenterY": 180,
	# 		},
	# 	],
	# 	"sounds": [],
	# 	"volume": 0,
	# 	"layerOrder": 0,

	# 	"tempo": 0,
	# 	"videoTransparency": 0,
	# 	"videoState": "off",
	# }

	# project = {
	# 	"targets": [stage],
	# 	"monitors": monitors,
	# 	"meta": {
	# 		"semver": "3.0.0",
	# 		"vm": "0.0.0",
	# 		"agent": "",
	# 	},
	# }

	# createProjectFiles(project)

# def md5sum(filename):
	# with open(filename, "rb") as f:
	# 	return md5(f.read()).hexdigest()

# def createProjectFiles(project):
	# try:
	# 	shutil.rmtree("project")
	# except FileNotFoundError:
	# 	pass
	# os.mkdir("project")

	# with open("project/project.json", "w+") as f:
	# 	f.write(dumps(project))

	# shutil.copy("resources/backdrop.svg",
	# 		"project/%s.svg" % project["targets"][0]["costumes"][0]["assetId"])

	# os.system("zip --quiet -r project.sb3 project")
	# shutil.rmtree("project")

if __name__ == "__main__":
	main()
