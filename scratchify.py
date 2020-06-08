from typing import Callable

currID = 0
def nextID() -> str:
	global currID
	currID += 1
	return f"_{currID}"

def resolve_var(name: str, env) -> str:
	for i in env["sprite"]["variables"]:
		if i["name"] == name:
			return i["id"]
	for i in env["stage"]["variables"]:
		if i["name"] == name:
			return i["id"]
	raise NameError(f"Identifier '{name}' is not defined")

def resolve_var_or_arr(name: str, env) -> str:
	for i in env["sprite"]["variables"]:
		if i["name"] == name:
			return "var", i["id"]
	for i in env["sprite"]["lists"]:
		if i["name"] == name:
			return "arr", i["id"]
	for i in env["stage"]["variables"]:
		if i["name"] == name:
			return "var", i["id"]
	for i in env["stage"]["lists"]:
		if i["name"] == name:
			return "arr", i["id"]
	raise NameError(f"Identifier '{name}' is not defined")

def resolve_proc(name: str, env) -> str:
	for i in env["sprite"]["procedures"]:
		if i["name"] == name:
			return i
	raise NameError(f"Identifier '{name}' is not defined")

def scratchify(tree, env=None) -> list:
	if type(tree) is dict:
		def assign_parent(parent_id: str, *args):
			for i in args:
				if type(i[0]) is tuple:
					i[0][1]["parent"] = parent_id

		def doubly_link_stms(first: tuple, rest: list):
			if len(rest):
				rest[0][0][1]["parent"] = first[0]
				for i in range(len(rest) - 1):
					rest[i][0][1]["next"] = rest[i + 1][0][0]
					rest[i + 1][0][1]["parent"] = rest[i][0][0]

		def stage_def(t: dict) -> list:
			return sum((
				scratchify(i, env)
				for i in t["procedures"]), [])

		def sprite_def(t: dict) -> list:
			return sum((
				scratchify(i, env)
				for i in t["procedures"]), [])

		def procedures_definition(t: dict) -> list:
			t["id"] = nextID()

			params = [
					scratchify(i, env)[0]
					for i in t["params"]]

			definition = (t["id"], {
				"opcode": "procedures_definition",
				"next": None,
				"parent": None,
				"inputs": {
					"custom_block": [1, nextID()]},
				"fields": {},
				"shadow": False,
				"topLevel": True,
				"x": 0,
				"y": 0})

			prototype = (definition[1]["inputs"]["custom_block"][1], {
				"opcode": "procedures_prototype",
				"next": None,
				"parent": definition[0],
				"inputs": {
					nextID(): [1, i[0]]
					for i in params},
				"fields": {},
				"shadow": True,
				"topLevel": False,
				"mutation": {
					"tagName": "mutation",
					"children": [],
					"proccode": t["name"] + " %s" * len(params),
					"argumentids": None,
					"argumentnames": str([
						i["name"]
						for i in t["params"]]).replace("'", "\""),
					"argumentdefaults":
					str([""] * len(params)).replace("'", "\""),
					"warp": t["warp"]}})

			body = [
					scratchify(i, env)
					for i in t["body"]]
			if len(body):
				definition[1]["next"] = body[0][0][0]

			prototype[1]["mutation"]["argumentids"] = str(list(
				prototype[1]["inputs"])).replace("'", "\"")

			for i in params:
				i[1]["parent"] = prototype[0]

			doubly_link_stms(definition, body)

			t["prototype"] = prototype

			params.append(definition)
			params.append(prototype)
			return sum(body, params)

		def param(t: dict) -> list:
			t["id"] = nextID()
			return [(t["id"], {
				"opcode": "argument_reporter_string_number",
				"next": None,
				"parent": None,
				"inputs": {},
				"fields": {
					"VALUE": [
						t["name"], None]},
				"shadow": False,
				"topLevel": False})]

		def motion_movesteps(t: dict) -> list:
			t["id"] = nextID()
			steps = scratchify(t["STEPS"], env)
			assign_parent(t["id"], steps)
			return [(t["id"], {
				"opcode": "motion_movesteps",
				"next": None,
				"parent": None,
				"inputs": {
					"STEPS": [1, steps[0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})] + steps

		def motion_gotoxy(t: dict) -> list:
			t["id"] = nextID()
			x = scratchify(t["X"], env)
			y = scratchify(t["Y"], env)
			assign_parent(t["id"], x, y)
			return [(t["id"], {
				"opcode": "motion_gotoxy",
				"next": None,
				"parent": None,
				"inputs": {
					"X": [1, x[0][0]],
					"Y": [1, y[0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})] + x + y

		def motion_turnright(t: dict) -> dict:
			t["id"] = nextID()
			degrees = scratchify(t["DEGREES"], env)
			assign_parent(t["id"], degrees)
			return [(t["id"], {
				"opcode": "motion_turnright",
				"next": None,
				"parent": None,
				"inputs": {
					"DEGREES": [1, degrees[0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})] + degrees

		def motion_turnleft(t: dict) -> dict:
			t["id"] = nextID()
			degrees = scratchify(t["DEGREES"], env)
			assign_parent(t["id"], degrees)
			return [(t["id"], {
				"opcode": "motion_turnleft",
				"next": None,
				"parent": None,
				"inputs": {
					"DEGREES": [1, degrees[0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})] + degrees

		def motion_ifonedgebounce(t: dict) -> list:
			t["id"] = nextID()
			return [(t["id"], {
				"opcode": "motion_ifonedgebounce",
				"next": None,
				"parent": None,
				"inputs": {},
				"fields": {},
				"shadow": False,
				"topLevel": False})]

		def motion_pointindirection(t: dict) -> list:
			t["id"] = nextID()
			direction = scratchify(t["DIRECTION"], env)
			assign_parent(t["id"], direction)
			return [(t["id"], {
				"opcode": "motion_pointindirection",
				"next": None,
				"parent": None,
				"inputs": {
					"DIRECTION": [1, direction[0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})] + direction

		def motion_glidesecstoxy(t: dict) -> list:
			t["id"] = nextID()
			x = scratchify(t["X"], env)
			y = scratchify(t["Y"], env)
			secs = scratchify(t["SECS"], env)
			assign_parent(t["id"], x, y, secs)
			return [(t["id"], {
				"opcode": "motion_glidesecstoxy",
				"next": None,
				"parent": None,
				"inputs": {
					"X": [1, x[0][0]],
					"Y": [1, y[0][0]],
					"SECS": [1, secs[0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})] + x + y + secs

		def control_if(t: dict) -> list:
			t["id"] = nextID()

			condition = scratchify(t["CONDITION"], env)
			assign_parent(t["id"], condition)

			substack = [
					scratchify(i, env)
					for i in t["true_branch"]]

			if_stmt = (t["id"], {
				"opcode": "control_if",
				"next": None,
				"parent": None,
				"inputs": {
					"CONDITION": [2, condition[0][0]],
					"SUBSTACK": [2, substack[0][0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})

			doubly_link_stms(if_stmt, substack)

			return sum(substack, [if_stmt] + condition)

		def control_if_else(t: dict) -> list:
			t["id"] = nextID()

			condition = scratchify(t["CONDITION"], env)
			assign_parent(t["id"], condition)

			substack = [
					scratchify(i, env)
					for i in t["true_branch"]]
			substack2 = [
					scratchify(i, env)
					for i in t["false_branch"]]

			if_stmt = (t["id"], {
				"opcode": "control_if_else",
				"next": None,
				"parent": None,
				"inputs": {
					"CONDITION": [2, condition[0][0]],
					"SUBSTACK": [2, substack[0][0][0]],
					"SUBSTACK2": [2, substack2[0][0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})

			doubly_link_stms(if_stmt, substack)
			doubly_link_stms(if_stmt, substack2)

			return sum(substack + substack2, [if_stmt] + condition)

		def control_repeat(t: dict) -> list:
			t["id"] = nextID()

			times = scratchify(t["TIMES"], env)
			assign_parent(t["id"], times)

			substack = [
					scratchify(i, env)
					for i in t["body"]]

			loop = (t["id"], {
				"opcode": "control_repeat",
				"next": None,
				"parent": None,
				"inputs": {
					"TIMES": [1, times[0][0]],
					"SUBSTACK": [2, substack[0][0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})

			doubly_link_stms(loop, substack)

			return sum(substack, [loop] + times)

		def control_forever(t: dict) -> list:
			t["id"] = nextID()

			substack = [
					scratchify(i, env)
					for i in t["body"]]

			loop = (t["id"], {
				"opcode": "control_forever",
				"next": None,
				"parent": None,
				"inputs": {
					"SUBSTACK": [2, substack[0][0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})

			doubly_link_stms(loop, substack)

			return sum(substack, [loop])

		def control_while(t: dict) -> list:
			t["id"] = nextID()

			condition = scratchify(t["CONDITION"], env)
			assign_parent(t["id"], condition)

			substack = [
					scratchify(i, env)
					for i in t["body"]]

			loop = (t["id"], {
				"opcode": "control_while",
				"next": None,
				"parent": None,
				"inputs": {
					"CONDITION": [2, condition[0][0]],
					"SUBSTACK": [2, substack[0][0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})

			doubly_link_stms(loop, substack)

			return sum(substack, [loop] + condition)

		def control_repeat_until(t: dict) -> list:
			t["id"] = nextID()

			condition = scratchify(t["CONDITION"], env)
			assign_parent(t["id"], condition)

			substack = [
					scratchify(i, env)
					for i in t["body"]]

			loop = (t["id"], {
				"opcode": "control_repeat_until",
				"next": None,
				"parent": None,
				"inputs": {
					"CONDITION": [2, condition[0][0]],
					"SUBSTACK": [2, substack[0][0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})

			doubly_link_stms(loop, substack)

			return sum(substack, [loop] + condition)

		def bin_numeric_op(op: str) -> Callable:
			def f(t):
				t["id"] = nextID()
				num1 = scratchify(t["NUM1"], env)
				num2 = scratchify(t["NUM2"], env)
				assign_parent(t["id"], num1, num2)
				return [(t["id"], {
					"opcode": op,
					"next": None,
					"parent": None,
					"inputs": {
						"NUM1": [1, num1[0][0]],
						"NUM2": [1, num2[0][0]]},
					"fields": {},
					"shadow": False,
					"topLevel": False})] + num1 + num2
			return f

		def binary_logic_operator(op: str) -> Callable:
			def f(t):
				t["id"] = nextID()
				operand1 = scratchify(t["OPERAND1"], env)
				operand2 = scratchify(t["OPERAND2"], env)
				assign_parent(t["id"], operand1, operand2)
				return [(t["id"], {
					"opcode": op,
					"next": None,
					"parent": None,
					"inputs": {
						"OPERAND1": [1, operand1[0][0]],
						"OPERAND2": [1, operand2[0][0]]},
					"fields": {},
					"shadow": False,
					"topLevel": False})] + operand1 + operand2
			return f

		def operator_not(t: dict) -> list:
			t["id"] = nextID()
			operand = scratchify(t["OPERAND"], env)
			assign_parent(t["id"], operand)
			return [(t["id"], {
				"opcode": "operator_not",
				"next": None,
				"parent": None,
				"inputs": {
					"OPERAND": [1, high[0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})] + operand

		def operator_random(t: dict) -> list:
			t["id"] = nextID()
			low = scratchify(t["FROM"], env)
			high = scratchify(t["TO"], env)
			assign_parent(t["id"], low, high)
			return [(t["id"], {
				"opcode": "operator_random",
				"next": None,
				"parent": None,
				"inputs": {
					"FROM": [1, low[0][0]],
					"TO": [1, high[0][0]]},
				"fields": {},
				"shadow": False,
				"topLevel": False})] + low + high

		def data_setvariableto(t: dict) -> list:
			t["id"] = nextID()
			var_id = resolve_var(t["name"], env)
			value = scratchify(t["value"], env)
			return [(t["id"], {
				"opcode": "data_setvariableto",
				"next": None,
				"parent": None,
				"inputs": {
					"VALUE": [1, value[0][0]]},
				"fields": {
					"VARIABLE": [
						t["name"],
						var_id]},
				"shadow": False,
				"topLevel": False})] + value

		def data_changevariableby(t: dict) -> list:
			t["id"] = nextID()
			var_or_arr, var_id = resolve_var_or_arr(t["name"], env)
			value = scratchify(t["value"], env)
			if var_or_arr == "var":
				return [(t["id"], {
					"opcode": "data_changevariableby",
					"next": None,
					"parent": None,
					"inputs": {
						"VALUE": [1, value[0][0]]},
					"fields": {
						"VARIABLE": [
							t["name"],
							var_id]},
					"shadow": False,
					"topLevel": False})] + value
			else:
				return [(t["id"], {
					"opcode": "data_addtolist",
					"next": None,
					"parent": None,
					"inputs": {
						"ITEM": [1, value[0][0]]},
					"fields": {
						"LIST": [
							t["name"],
							var_id]},
					"shadow": False,
					"topLevel": False})] + value

		def procedures_call(t: dict) -> list:
			# TODO Finish this function
			t["id"] = nextID()

			proc = resolve_proc(t["name"], env)
			args = [
					scratchify(i, env)
					for i in t["args"]]
			call = [(t["id"], {
				"opcode": "procedures_call",
				"next": None,
				"parent": None,
				"inputs": {
					i: [1, j[0][0]]
					for i, j in zip(proc["prototype"][1]["inputs"], args)},
				"fields": {},
				"shadow": False,
				"topLevel": False,
				"mutation": {
					"tagName": "mutation",
					"children": [],
					"proccode": t["name"] + " %s" * len(proc["params"]),
					"argumentids": str([
						i
						for i in proc["prototype"][1]["inputs"]])\
								.replace("'", "\""),
					"warp": proc["warp"]}})]
			return sum(args, call)

		def ident(t: dict) -> list:
			var_or_arr, var_id = resolve_var_or_arr(t["name"], env)
			return [[[
				12 if var_or_arr == "var" else 13,
				t["name"], var_id]]]

		def program(t: dict) -> list:
			for i in t["stage"]["variables"]:
				i["id"] = nextID()
			for i in t["stage"]["lists"]:
				i["id"] = nextID()

			stage = {
				"isStage": True,
				"name": "Stage",
				"variables": {
					i["id"]: [i["name"], 0]
					for i in t["stage"]["variables"]},
				"lists": {
					i["id"]: [i["name"], []]
					for i in t["stage"]["lists"]},
				"broadcasts": {},
				"blocks": dict(
					i
					for i in scratchify(t["stage"], env or {
						"stage": t["stage"],
						"sprite": t["stage"]})
					if type(i) is tuple),
				"comments": {},
				"currentCostume": 0,
				"costumes": [],
				"sounds": [],
				"volume": 0,
				"layerOrder": 0,

				"tempo": 0,
				"videoTransparency": 0,
				"videoState": "off"}

			targets = [stage]
			for i, spr in enumerate(t["sprites"]):
				for j in spr["variables"]:
					j["id"] = nextID()
				for j in spr["lists"]:
					j["id"] = nextID()

				targets.append({
					"isStage": False,
					"name": spr["name"],
					"variables": {
						j["id"]: [j["name"], 0]
						for j in spr["variables"]},
					"lists": {
						j["id"]: [j["name"], []]
						for j in spr["lists"]},
					"broadcasts": {},
					"blocks": dict(
						j
						for j in scratchify(spr, env or {
							"stage": t["stage"],
							"sprite": spr})
						if type(j) is tuple),
					"comments": {},
					"currentCostume": 0,
					"costumes": [],
					"sounds": [],
					"volume": 0,
					"layerOrder": i + 1,

					"visible": True,
					"x": 0,
					"y": 0,
					"size": 100,
					"direction": 90,
					"draggable": False,
					"rotationStyle": "all around"})

			project = {
				"targets": targets,
				"monitors": [],
				"meta": {
					"semver": "3.0.0",
					"vm": "0.0.0",
					"agent": ""}}

			return project

		return {
				"operator_add": bin_numeric_op("operator_add"),
				"operator_subtract": bin_numeric_op("operator_subtract"),
				"operator_multiply": bin_numeric_op("operator_multiply"),
				"operator_divide": bin_numeric_op("operator_divide"),
				"operator_mod": bin_numeric_op("operator_mod"),
				"operator_equals": binary_logic_operator("operator_equals"),
				"operator_gt": binary_logic_operator("operator_gt"),
				"operator_lt": binary_logic_operator("operator_lt"),
				"operator_and": binary_logic_operator("operator_and"),
				"operator_or": binary_logic_operator("operator_or"),
				"operator_not": operator_not,
				"operator_random": operator_random,
				"procedures_definition": procedures_definition,
				"procedures_call": procedures_call,
				"control_if": control_if,
				"control_if_else": control_if_else,
				"control_forever": control_forever,
				"control_while": control_while,
				"control_repeat_until": control_repeat_until,
				"control_repeat": control_repeat,
				"data_setvariableto": data_setvariableto,
				"data_changevariableby": data_changevariableby,
				"ident": ident,
				"stage_def": stage_def,
				"sprite_def": sprite_def,
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
	elif type(tree) in (int, float):
		return [[[4, tree]]]
	elif type(tree) is str:
		return [[[10, tree]]]
	else:
		return tree
