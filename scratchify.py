def scratchify(tree):
	if type(tree) is dict:
		def expect_args(name, count, provided):
			if count != provided:
				raise Exception(f"{name} expected {count} arguments but \
						{provided} were provided")
		def func_call(t):
			def unary_func(operator):
				def f(u):
					expect_args(operator, 1, len(u["args"]))
					return {"type": "mathop",
							"operator": operator,
							"NUM": u["args"][0]}
				return f

			def unknown_func(u):
				raise Exception(f"The function {u['name']} does not exist")

			return {
					"abs": unary_func("abs"),
					"floor": unary_func("floor"),
					"ceiling": unary_func("ceiling"),
					"sqrt": unary_func("sqrt"),
					"sin": unary_func("sin"),
					"cos": unary_func("cos"),
					"tan": unary_func("tan"),
					"asin": unary_func("asin"),
					"acos": unary_func("acos"),
					"atan": unary_func("atan"),
					"ln": unary_func("ln"),
					"log": unary_func("log"),
					"exp": unary_func("e ^"),
					"pow": unary_func("10 ^"),
					}.get(t["name"], unknown_func)(t)

		def basic_scratchify(*args):
			def f(t):
				for i in args:
					t[i] = scratchify(t[i])
				return t
			return f

		return {
				"operator_add": basic_scratchify("NUM1", "NUM2"),
				"operator_subtract": basic_scratchify("NUM1", "NUM2"),
				"operator_multiply": basic_scratchify("NUM1", "NUM2"),
				"operator_divide": basic_scratchify("NUM1", "NUM2"),
				"operator_mod": basic_scratchify("NUM1", "NUM2"),
				"operator_equals": basic_scratchify("OPERAND1", "OPERAND2"),
				"operator_gt": basic_scratchify("OPERAND1", "OPERAND2"),
				"operator_lt": basic_scratchify("OPERAND1", "OPERAND2"),
				"operator_and": basic_scratchify("OPERAND1", "OPERAND2"),
				"operator_or": basic_scratchify("OPERAND1", "OPERAND2"),
				"operator_not": basic_scratchify("OPERAND"),
				"procedures_definition": basic_scratchify("body"),
				"procedures_call": basic_scratchify("args"),
				"func_call": func_call,
				"control_if": basic_scratchify("CONDITION", "true_branch"),
				"control_if_else": basic_scratchify("CONDITION", "true_branch",
					"false_branch"),
				"control_forever": basic_scratchify("body"),
				"control_while": basic_scratchify("CONDITION", "body"),
				"control_repeat_until": basic_scratchify("CONDITION", "body"),
				"control_repeat": basic_scratchify("TIMES", "body"),
				"data_setvariableto": basic_scratchify("value"),
				"data_changevariableby": basic_scratchify("value"),
				"scene_def": basic_scratchify("procedures"),
				"sprite_def": basic_scratchify("procedures"),
				"program": basic_scratchify("scene", "sprites"),
				}.get(tree["type"], lambda x: x)(tree)
	elif type(tree) is list:
		l = []
		for i in tree:
			i = scratchify(i)
			if type(i) is list:
				l += i
			elif i is not None:
				l.append(i)
		return l
	else:
		return tree
