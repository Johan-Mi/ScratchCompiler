from math import isnan

def toBool(v):
	if type(v) is bool:
		return v
	if type(v) is str:
		return v.lower() not in ("", "0", "false")
	return bool(v)

def toNumber(v):
	if type(v) is int or type(v) is float:
		return 0 if isnan(v) else v
	try:
		n = float(v)
		return 0 if isnan(n) else n
	except ValueError:
		return 0

def optimize(tree):
	if type(tree) is dict:
		def bin_numeric_op(func):
			def f(t):
				t["NUM1"] = optimize(t["NUM1"])
				t["NUM2"] = optimize(t["NUM2"])
				if type(t["NUM1"]) is dict or type(t["NUM2"]) is dict:
					return t
				else:
					return func(toNumber(t["NUM1"]), toNumber(t["NUM2"]))
			return f

		operator_add = bin_numeric_op(lambda a, b: a + b)
		operator_subtract = bin_numeric_op(lambda a, b: a - b)
		operator_multiply = bin_numeric_op(lambda a, b: a * b)
		operator_divide = bin_numeric_op(lambda a, b: a / b)
		operator_mod = bin_numeric_op(lambda a, b: a % b)

		def operator_equals(t):
			t["OPERAND1"] = optimize(t["OPERAND1"])
			t["OPERAND2"] = optimize(t["OPERAND2"])
			if type(t["OPERAND1"]) is dict or type(t["OPERAND2"]) is dict:
				return t
			else:
				a = t["OPERAND1"]
				b = t["OPERAND2"]
				if type(b) is not type(a):
					b = type(a)(b)
				return str(a == b).lower()

		def operator_lt(t):
			t["OPERAND1"] = optimize(t["OPERAND1"])
			t["OPERAND2"] = optimize(t["OPERAND2"])
			if type(t["OPERAND1"]) is dict or type(t["OPERAND2"]) is dict:
				return t
			else:
				a = t["OPERAND1"]
				b = t["OPERAND2"]
				if type(b) is not type(a):
					b = type(a)(b)
				return str(a < b).lower()

		def operator_gt(t):
			t["OPERAND1"] = optimize(t["OPERAND1"])
			t["OPERAND2"] = optimize(t["OPERAND2"])
			if type(t["OPERAND1"]) is dict or type(t["OPERAND2"]) is dict:
				return t
			else:
				a = t["OPERAND1"]
				b = t["OPERAND2"]
				if type(b) is not type(a):
					b = type(a)(b)
				return str(a > b).lower()

		def procedures_definition(t):
			t["body"] = optimize(t["body"])
			return t

		def procedures_call(t):
			t["args"] = optimize(t["args"])
			return t

		def control_if(t):
			t["CONDITION"] = optimize(t["CONDITION"])
			t["true_branch"] = [optimize(i) for i in t["true_branch"]]
			if type(t["CONDITION"]) is dict:
				return t
			else:
				if toBool(t["CONDITION"]):
					return t["true_branch"]
				else:
					return None

		def control_if_else(t):
			t["CONDITION"] = optimize(t["CONDITION"])
			t["true_branch"] = [optimize(i) for i in t["true_branch"]]
			t["false_branch"] = [optimize(i) for i in t["false_branch"]]
			if type(t["CONDITION"]) is dict:
				return t
			else:
				if toBool(t["CONDITION"]):
					return t["true_branch"]
				else:
					return t["false_branch"]

		def control_forever(t):
			t["body"] = optimize(t["body"])
			return t

		def control_while(t):
			t["CONDITION"] = optimize(t["CONDITION"])
			t["body"] = optimize(t["body"])
			if type(t["CONDITION"]) is dict:
				return t
			else:
				if toBool(t["CONDITION"]):
					return {"type": "control_forever",
							"body": t["body"]}
				else:
					return None

		def control_repeat_until(t):
			t["CONDITION"] = optimize(t["CONDITION"])
			t["body"] = optimize(t["body"])
			if type(t["CONDITION"]) is dict:
				return t
			else:
				if toBool(t["CONDITION"]):
					return None
				else:
					return {"type": "control_forever",
							"body": t["body"]}

		def data_setvariableto(t):
			t["value"] = optimize(t["value"]);
			return t

		def data_changevariableby(t):
			t["value"] = optimize(t["value"]);
			return t

		def scene_def(t):
			t["procedures"] = optimize(t["procedures"])
			return t

		def sprite_def(t):
			t["procedures"] = optimize(t["procedures"])
			return t

		def program(t):
			t["scene"] = optimize(t["scene"])
			t["sprites"] = optimize(t["sprites"])
			return t

		return {
				"operator_add": operator_add,
				"operator_subtract": operator_subtract,
				"operator_multiply": operator_multiply,
				"operator_divide": operator_divide,
				"operator_mod": operator_mod,
				"operator_equals": operator_equals,
				"procedures_definition": procedures_definition,
				"procedures_call": procedures_call,
				"control_if": control_if,
				"control_if_else": control_if_else,
				"control_forever": control_forever,
				"control_while": control_while,
				"control_repeat_until": control_repeat_until,
				"data_setvariableto": data_setvariableto,
				"data_changevariableby": data_changevariableby,
				"scene_def": scene_def,
				"sprite_def": sprite_def,
				"program": program,
				}.get(tree["type"], lambda x: x)(tree)
	elif type(tree) is list:
		l = []
		for i in tree:
			i = optimize(i)
			if type(i) is list:
				l += i
			elif i is not None:
				l.append(i)
		return l
	else:
		return tree
