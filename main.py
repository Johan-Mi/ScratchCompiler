#!/usr/bin/env python3

import os
import json
import shutil
import hashlib

def md5sum(filename):
	with open(filename, "rb") as f:
		return hashlib.md5(f.read()).hexdigest()

def main():
	backdropMd5 = md5sum("resources/backdrop.svg")

	variables = {}

	lists = {}

	stage = {
		"isStage": True,
		"name": "Stage",
		"variables": variables,
		"lists": lists,
		"broadcasts": {},
		"blocks": {},
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
		"videoState": "on",
		"textToSpeechLanguage": None,
	}

	targets = [
		stage,
	]

	project = {
		"targets": targets,
		"monitors": [],
		"extensions": [],
		"meta": {
			"semver": "3.0.0",
			"vm": "0.0.0-prerelease.00000000000000",
			"agent": "-",
		},
	}

	createProjectFiles(project)

def createProjectFiles(project):
	shutil.rmtree("project")
	os.mkdir("project")

	with open("project/project.json", "w+") as f:
		f.write(json.dumps(project))

	shutil.copy("resources/backdrop.svg",
			"project/%s.svg" % project["targets"][0]["costumes"][0]["assetId"])

	try:
		os.remove("project.sb3")
	except FileNotFoundError:
		pass

	os.system("zip -r project.sb3 project")

if __name__ == "__main__":
	main()
