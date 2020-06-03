from functools import reduce
import operator

currID = 0

def nextID():
	global currID
	currID += 1
	return f"_{currID}"

def scratchify(tree, env=None):
	if type(tree) is dict:
		def stage_def(t):
			return reduce(operator.add,
					(scratchify(i, env) for i in t["procedures"]), [])

		def procedures_definition(t):
			params = [scratchify(i, env)[0] for i in t["params"]]
			definition = (nextID(), {
				"opcode": "procedures_definition",
				"next": None,
				"parent": None,
				"inputs": {
					"custom_block": [1, 0]
					},
				"fields": {},
				"shadow": False,
				"topLevel": True,
				"x": 0,
				"y": 0,
				})
			prototype = (nextID(), {
				"opcode": "procedures_prototype",
				"next": None,
				"parent": definition[0],
				"inputs": {nextID(): [1, i[0]] for i in params},
				"fields": {},
				"shadow": True,
				"topLevel": False,
				"mutation": {
					"tagName": "mutation",
					"children": [],
					"proccode": t['name'] + " %s" * len(params),
					"argumentids": None,
					"argumentnames":
					str([i["name"] for i in t["params"]]).replace("'", "\""),
					"argumentdefaults":
					str([""] * len(params)).replace("'", "\""),
					"warp": t["warp"],
					}
				})
			prototype[1]["mutation"]["argumentids"] = \
					str([i for i in prototype[1]["inputs"]]).replace("'", "\"")
			definition[1]["inputs"]["custom_block"][1] = prototype[0]
			for i in params:
				i[1]["parent"] = prototype[0]

			body = reduce(operator.add, [scratchify(i) for i in t["body"]])
			definition[1]["next"] = body[0][0]
			for i in range(1, len(body)):
				body[i][1]["parent"] = body[i - 1][0]
			for i in range(len(body) - 1):
				body[i][1]["next"] = body[i + 1][0]
			body[0][1]["parent"] = definition[0]
			# print(body)

			params.append(definition)
			params.append(prototype)
			params += body
			return params

		def param(t):
			t["id"] = nextID()
			return [(t["id"], {
				"opcode": "argument_reporter_string_number",
				"next": None,
				"parent": None,
				"inputs": {},
				"fields": {
					"VALUE": [
						t["name"], None
						]
					},
				"shadow": False,
				"topLevel": False,
				})]

		def motion_movesteps(t):
			t["id"] = nextID()
			return [(t["id"], {
				"opcode": "motion_movesteps",
				"next": None,
				"parent": None,
				"inputs": {
					"STEPS": [1, scratchify(t["STEPS"])],
					},
				"fields": {},
				"shadow": False,
				"topLevel": False,
				})]

		def motion_gotoxy(t):
			t["id"] = nextID()
			return [(t["id"], {
				"opcode": "motion_gotoxy",
				"next": None,
				"parent": None,
				"inputs": {
					"X": [1, scratchify(t["X"])],
					"Y": [1, scratchify(t["Y"])],
					},
				"fields": {},
				"shadow": False,
				"topLevel": False,
				})]

		def motion_turnright(t):
			t["id"] = nextID()
			return [(t["id"], {
				"opcode": "motion_turnright",
				"next": None,
				"parent": None,
				"inputs": {
					"DEGREES": [1, scratchify(t["DEGREES"])],
					},
				"fields": {},
				"shadow": False,
				"topLevel": False,
				})]

		def motion_turnleft(t):
			t["id"] = nextID()
			return [(t["id"], {
				"opcode": "motion_turnleft",
				"next": None,
				"parent": None,
				"inputs": {
					"DEGREES": [1, scratchify(t["DEGREES"])],
					},
				"fields": {},
				"shadow": False,
				"topLevel": False,
				})]

		def motion_ifonedgebounce(t):
			t["id"] = nextID()
			return [(t["id"], {
				"opcode": "motion_ifonedgebounce",
				"next": None,
				"parent": None,
				"inputs": {},
				"fields": {},
				"shadow": False,
				"topLevel": False,
				})]

		def motion_pointindirection(t):
			t["id"] = nextID()
			return [(t["id"], {
				"opcode": "motion_pointindirection",
				"next": None,
				"parent": None,
				"inputs": {
					"DIRECTION": [1, scratchify(t["DIRECTION"])],
					},
				"fields": {},
				"shadow": False,
				"topLevel": False,
				})]

		def motion_glidesecstoxy(t):
			t["id"] = nextID()
			return [(t["id"], {
				"opcode": "motion_glidesecstoxy",
				"next": None,
				"parent": None,
				"inputs": {
					"X": [1, scratchify(t["X"])],
					"Y": [1, scratchify(t["Y"])],
					"SECS": [1, scratchify(t["SECS"])],
					},
				"fields": {},
				"shadow": False,
				"topLevel": False,
				})]

		def program(t):
			stage = {
				"isStage": True,
				"name": "Stage",
				"variables": { f"var_{name}": [name, 0]
					for name in t["stage"]["variables"]},
				"lists": { f"arr_{name}": [name, []]
					for name in t["stage"]["lists"]},
				"broadcasts": {},
				"blocks": dict(scratchify(t["stage"], env or t)),
				"comments": {},
				"currentCostume": 0,
				"costumes": [],
				"sounds": [],
				"volume": 0,
				"layerOrder": 0,

				"tempo": 0,
				"videoTransparency": 0,
				"videoState": "off",
			}

			targets = [stage]
			# for i in t["sprites"]:
			# 	spr = {
			# 		"isStage": False,
			# 		"name": i["name"],
			# 		"variables": { "var_%s" % name : [name, 0]
			# 			for name in i["variables"]},
			# 		"lists": { "arr_%s" % name : [name, []]
			# 			for name in i["lists"]},
			# 		"broadcasts": {},
			# 		"blocks": {},
			# 		"comments": {},
			# 		"currentCostume": 0,
			# 		"costumes": [],
			# 		"sounds": [],
			# 		"volume": 0,
			# 		"layerOrder": 0,
			# 	}
			# 	targets.append(spr)

			project = {
				"targets": targets,
				"monitors": [],
				"meta": {
					"semver": "3.0.0",
					"vm": "0.0.0",
					"agent": "",
				},
			}

			return project

		return {
				# "operator_add": nop,
				# "operator_subtract": nop,
				# "operator_multiply": nop,
				# "operator_divide": nop,
				# "operator_mod": nop,
				# "operator_equals": nop,
				# "operator_gt": nop,
				# "operator_lt": nop,
				# "operator_and": nop,
				# "operator_or": nop,
				# "operator_not": nop,
				"procedures_definition": procedures_definition,
				# "procedures_call": nop,
				# "func_call": nop,
				# "control_if": nop,
				# "control_if_else": nop,
				# "control_forever": nop,
				# "control_while": nop,
				# "control_repeat_until": nop,
				# "control_repeat": nop,
				# "data_setvariableto": nop,
				# "data_changevariableby": nop,
				"stage_def": stage_def,
				# "sprite_def": nop,
				"program": program,
				"param": param,
				"motion_movesteps": motion_movesteps,
				"motion_gotoxy": motion_gotoxy,
				"motion_turnright": motion_turnright,
				"motion_turnleft": motion_turnleft,
				"motion_pointindirection": motion_pointindirection,
				"motion_glidesecstoxy": motion_glidesecstoxy,
				"motion_ifonedgebounce": motion_ifonedgebounce,
				}.get(tree["type"], lambda x: [])(tree)
	# elif type(tree) is list:
	# 	return reduce(operator.add, tree, [])
	elif type(tree) in (int, float):
		return [4, tree]
	else:
		return tree
