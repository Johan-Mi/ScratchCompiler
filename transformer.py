from lark import Transformer

class GrammarTransformer(Transformer):
	def start(args):
		scene = [i for i in args if i["type"] == "scene_def"]
		assert len(scene) <= 1
		scene = scene[0] if scene else {"type": "scene_def", "procedures": []}
		return {"type": "program",
				"variables":
				[i["name"] for i in args if i["type"] == "var_decl"],
				"lists": [i["name"] for i in args if i["type"] == "arr_decl"],
				"sprites": [i for i in args if i["type"] == "sprite_def"],
				"scene": scene}
	def scene_def(args):
		costumes = [i for i in args
				if type(i) is dict
				and i["type"] == "costume_list"]
		assert len(costumes) <= 1
		costumes = costumes[0]["costumes"] if costumes else []
		return {"type": "scene_def",
				"costumes": costumes,
				"procedures":
				[i for i in args
					if type(i) is dict
					and i["type"] == "procedures_definition"]}
	def sprite_def(args):
		costumes = [i for i in args
				if type(i) is dict
				and i["type"] == "costume_list"]
		assert len(costumes) <= 1
		costumes = costumes[0]["costumes"] if costumes else []
		return {"type": "sprite_def",
				"name": args[0]["name"],
				"costumes": costumes,
				"variables":
				[i["name"] for i in args if i["type"] == "var_decl"],
				"lists": [i["name"] for i in args if i["type"] == "arr_decl"],
				"procedures":
				[i for i in args if i["type"] == "procedures_definition"]}
	costume_list = lambda args: {"type": "costume_list",
			"costumes": args}
	ident = lambda args: {"type": "ident",
			"name": str(args[0])}
	stmts = lambda args: {"type": "stmts",
			"stmts": args}
	block_stmt = lambda args: {"type": "block_stmt",
			"body": args[0]}
	proc_def = lambda args: {"type": "procedures_definition",
			"name": args[0]["name"],
			"params": args[1]["params"],
			"body": args[2]["body"]["stmts"]}
	param_list = lambda args: {"type": "param_list",
			"params": [{"type": "param", "name": p["name"]} for p in args]}
	func_call = lambda args: {"type": "procedures_call",
			"name": args[0]["name"],
			"args": args[1]["args"]}
	number = lambda args: float(args[0])
	string = lambda args: args[0][1:-1]
	arg_list = lambda args: {"type": "arg_list",
			"args": args}
	addition = lambda args: {"type": "operator_add",
			"NUM1": args[0],
			"NUM2": args[1]}
	subtraction = lambda args: {"type": "operator_subtract",
			"NUM1": args[0],
			"NUM2": args[1]}
	multiplication = lambda args: {"type": "operator_multiply",
			"NUM1": args[0],
			"NUM2": args[1]}
	division = lambda args: {"type": "operator_divide",
			"NUM1": args[0],
			"NUM2": args[1]}
	modulo = lambda args: {"type": "operator_mod",
			"NUM1": args[0],
			"NUM2": args[1]}
	negate = lambda args: {"type": "operator_subtract",
			"NUM1": 0.0,
			"NUM2": args[0]}
	less_than = lambda args: {"type": "operator_lt",
			"OPERAND1": args[0],
			"OPERAND2": args[1]}
	greater_than = lambda args: {"type": "operator_gt",
			"OPERAND1": args[0],
			"OPERAND2": args[1]}
	equal_to = lambda args: {"type": "operator_equals",
			"OPERAND1": args[0],
			"OPERAND2": args[1]}
	logical_or = lambda args: {"type": "operator_or",
			"OPERAND1": args[0],
			"OPERAND2": args[1]}
	logical_and = lambda args: {"type": "operator_and",
			"OPERAND1": args[0],
			"OPERAND2": args[1]}
	logical_not = lambda args: {"type": "operator_not",
			"OPERAND": args[0]}
	var_decl = lambda args: {"type": "var_decl",
			"name": args[0]["name"]}
	arr_decl = lambda args: {"type": "arr_decl",
			"name": args[0]["name"]}
	if_stmt = lambda args: {"type": "control_if",
			"CONDITION": args[0],
			"true_branch": args[1]["body"]["stmts"]}
	if_else_stmt = lambda args: {"type": "control_if_else",
			"CONDITION": args[0],
			"true_branch": args[1]["body"]["stmts"],
			"false_branch": args[2]["body"]["stmts"]}
	if_elif_stmt = lambda args: {"type": "control_if_else",
			"CONDITION": args[0],
			"true_branch": args[1]["body"]["stmts"],
			"false_branch": [args[2]]}
	var_eq = lambda args: {"type": "data_setvariableto",
			"name": args[0]["name"],
			"value": args[1]}
	var_peq = lambda args: {"type": "data_changevariableby",
			"name": args[0]["name"],
			"value": args[1]}
	var_meq = lambda args: {"type": "data_changevariableby",
			"name": args[0]["name"],
			"value": {"type": "operator_subtract",
				"NUM1": 0.0,
				"NUM2": args[1]}}
	var_teq = lambda args: {"type": "data_setvariableto",
			"name": args[0]["name"],
			"value": {"type": "operator_multiply",
				"NUM1": args[0],
				"NUM2": args[1]}}
	var_deq = lambda args: {"type": "data_setvariableto",
			"name": args[0]["name"],
			"value": {"type": "operator_divide",
				"NUM1": args[0],
				"NUM2": args[1]}}
	until_loop = lambda args: {"type": "control_repeat_until",
			"CONDITION": args[0],
			"body": args[1]["body"]["stmts"]}
	while_loop = lambda args: {"type": "control_while",
			"CONDITION": args[0],
			"body": args[1]["body"]["stmts"]}
	repeat_loop = lambda args: {"type": "control_repeat",
			"TIMES": args[0],
			"body": args[1]["body"]["stmts"]}
	forever_loop = lambda args: {"type": "control_forever",
			"body": args[0]["body"]["stmts"]}
	true = lambda args: "true"
	false = lambda args: "false"
