from lark import Transformer

class GrammarTransformer(Transformer):
	def start(args):
		scene = [i for i in args if i["type"] == "scene_def"]
		if len(scene) > 1:
			raise Exception("Scene defined multiple times")
		scene = scene[0] if scene else {"type": "scene_def", "procedures": []}
		scene["variables"] = \
			[i["name"] for i in args if i["type"] == "var_decl"]
		scene["lists"] = [i["name"] for i in args if i["type"] == "arr_decl"]
		return {"type": "program",
				"scene": scene,
				"sprites": [i for i in args if i["type"] == "sprite_def"]}
	def scene_def(args):
		costumes = [i for i in args
				if type(i) is dict and i["type"] == "costume_list"]
		if len(costumes) > 1:
			raise Exception("Scene has multiple costume lists")
		costumes = costumes[0]["costumes"] if costumes else []
		return {"type": "scene_def",
				"costumes": costumes,
				"procedures":
				[i for i in args if type(i) is dict
					and i["type"] == "procedures_definition"]}
	def sprite_def(args):
		costumes = [i for i in args if type(i) is dict
				and i["type"] == "costume_list"]
		if len(costumes) > 1:
			raise Exception("Sprite has multiple costume lists")
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
	def func_call(args):
		def expect_args(name, count, provided):
			if count != provided:
				raise Exception(f"{name} expected {count} arguments but \
						{provided} were provided")

		def unary_math_func(operator):
			def f(u):
				expect_args(operator, 1, len(u["args"]))
				return {"type": "mathop",
						"OPERATOR": operator,
						"NUM": u["args"][0]}
			return f

		def unknown_func(u):
			raise Exception(f"The function {u['name']} does not exist")

		t = {"name": args[0]["name"],
				"args": args[1]["args"]}

		return {
				"abs": unary_math_func("abs"),
				"floor": unary_math_func("floor"),
				"ceiling": unary_math_func("ceiling"),
				"sqrt": unary_math_func("sqrt"),
				"sin": unary_math_func("sin"),
				"cos": unary_math_func("cos"),
				"tan": unary_math_func("tan"),
				"asin": unary_math_func("asin"),
				"acos": unary_math_func("acos"),
				"atan": unary_math_func("atan"),
				"ln": unary_math_func("ln"),
				"log": unary_math_func("log"),
				"exp": unary_math_func("e ^"),
				"pow": unary_math_func("10 ^"),
				}.get(t["name"], unknown_func)(t)
		# return {"type": "func_call",
		# 		"name": args[0]["name"],
		# 		"args": args[1]["args"]}
	procedures_call = lambda args: {"type": "procedures_call",
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
