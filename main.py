#!/usr/bin/env python3

import os
import json
import shutil
from hashlib import md5

def main():
	backdropMd5 = md5sum("resources/backdrop.svg")

	variables = {
		"foo": "bar",
		"hello": "there",
		"hotel": "trivago",
		"saved on car insurance by switching to Geico": 20,
	}

	lists = {
		"primes": [2, 3, 5, 7, 11],
		"squares": [1, "four", 9, 16, 25],
	}

	blocks = {}

	stage = {
		"isStage": True,
		"name": "Stage",
		"variables": { "var_%s" % name : [name, value]
			for name, value in variables.items() },
		"lists": { "var_%s" % name : [name, value]
			for name, value in lists.items() },
		"broadcasts": {},
		"blocks": blocks,
		"comments": {},
		"currentCostume": 0,
		"costumes": [
			{
				"assetId": backdropMd5,
				"name": "backdrop",
				"md5ext": "%s.svg" % backdropMd5,
				"dataFormat": "svg",
				"rotationCenterX": 240,
				"rotationCenterY": 180,
			},
		],
		"sounds": [],
		"volume": 0,
		"layerOrder": 0,

		"tempo": 0,
		"videoTransparency": 0,
		"videoState": "off",
	}

	targets = [
		stage,
	]

	project = {
		"targets": targets,
		"monitors": [],
		"meta": {
			"semver": "3.0.0",
			"vm": "0.0.0",
			"agent": "",
		},
	}

	createProjectFiles(project)

def md5sum(filename):
	with open(filename, "rb") as f:
		return md5(f.read()).hexdigest()

def createProjectFiles(project):
	try:
		shutil.rmtree("project")
	except FileNotFoundError:
		pass
	os.mkdir("project")

	with open("project/project.json", "w+") as f:
		f.write(json.dumps(project))

	shutil.copy("resources/backdrop.svg",
			"project/%s.svg" % project["targets"][0]["costumes"][0]["assetId"])

	os.system("zip --quiet -r project.sb3 project")
	shutil.rmtree("project")

if __name__ == "__main__":
	main()
