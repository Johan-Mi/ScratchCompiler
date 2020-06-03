import operator
import math
from cast import toBool, toNumber, toString

def optimize(tree):
	if type(tree) is dict:
		def basic_optimize(t, *args):
			for i in args:
				t[i] = optimize(t[i])

		def bin_numeric_op(func):
			def f(t):
				basic_optimize(t, "NUM1", "NUM2")
				if type(t["NUM1"]) is dict or type(t["NUM2"]) is dict:
					return t
				else:
					return func(toNumber(t["NUM1"]), toNumber(t["NUM2"]))
			return f

		def bin_equality_op(func):
			def f(t):
				basic_optimize(t, "OPERAND1", "OPERAND2")
				if type(t["OPERAND1"]) is dict or type(t["OPERAND2"]) is dict:
					return t
				else:
					a = t["OPERAND1"]
					b = t["OPERAND2"]
					if type(b) is not type(a):
						b = type(a)(b)
					return "true" if func(a, b) else "false"
			return f

		def operator_and(t):
			basic_optimize(t, "OPERAND1", "OPERAND2")
			if type(t["OPERAND1"]) is dict or type(t["OPERAND2"]) is dict:
				return t
			else:
				return "true" \
						if toBool(t["OPERAND1"]) and toBool(t["OPERAND2"]) \
						else "false"

		def operator_or(t):
			basic_optimize(t, "OPERAND1", "OPERAND2")
			if type(t["OPERAND1"]) is dict or type(t["OPERAND2"]) is dict:
				return t
			else:
				return "true" \
						if toBool(t["OPERAND1"]) or toBool(t["OPERAND2"]) \
						else "false"

		def operator_not(t):
			basic_optimize(t, "OPERAND")
			if type(t["OPERAND"]) is dict:
				return t
			else:
				return "false" if toBool(t["OPERAND"]) else "true"

		def operator_length(t):
			basic_optimize(t, "STRING")
			if type(t["STRING"]) is dict:
				return t
			else:
				return len(toString(t["STRING"]))

		def operator_join(t):
			basic_optimize(t, "STRING1", "STRING2")
			if type(t["STRING1"]) is dict or type(t["STRING2"]) is dict:
				return t
			else:
				return toString(t["STRING1"]) + toString(t["STRING2"])

		def operator_contains(t):
			basic_optimize(t, "STRING1", "STRING2")
			if type(t["STRING1"]) is dict or type(t["STRING2"]) is dict:
				return t
			else:
				return "true" if toString(t["STRING2"]).lower() in \
						toString(t["STRING1"]).lower() else "false"

		def procedures_definition(t):
			basic_optimize(t, "body")
			return t

		def procedures_call(t):
			basic_optimize(t, "args")
			return t

		def control_if(t):
			basic_optimize(t, "CONDITION", "true_branch")
			if type(t["CONDITION"]) is dict:
				return t
			else:
				return t["true_branch"] if toBool(t["CONDITION"]) else None

		def control_if_else(t):
			basic_optimize(t, "CONDITION", "true_branch", "false_branch")
			if type(t["CONDITION"]) is dict:
				return t
			else:
				return t["true_branch" if toBool(t["CONDITION"]) else
						"false_branch"]

		def control_forever(t):
			basic_optimize(t, "body")
			return t

		def control_while(t):
			basic_optimize(t, "CONDITION", "body")
			if type(t["CONDITION"]) is dict:
				return t
			else:
				return {"type": "control_forever",
						"body": t["body"]} if toBool(t["CONDITION"]) else None

		def control_repeat_until(t):
			basic_optimize(t, "CONDITION", "body")
			if type(t["CONDITION"]) is dict:
				return t
			else:
				return None if toBool(t["CONDITION"]) \
						else {"type": "control_forever",
								"body": t["body"]}

		def control_repeat(t):
			basic_optimize(t, "TIMES", "body")
			return t

		def data_setvariableto(t):
			basic_optimize(t, "value")
			return t

		def data_changevariableby(t):
			basic_optimize(t, "value")
			return t

		def stage_def(t):
			basic_optimize(t, "procedures")
			return t

		def sprite_def(t):
			basic_optimize(t, "procedures")
			return t

		def program(t):
			basic_optimize(t, "stage", "sprites")
			return t

		def mathop(t):
			basic_optimize(t, "NUM")
			if type(t["NUM"]) is dict:
				return t
			else:
				return {
						"abs": abs,
						"floor": math.floor,
						"ceiling": math.ceil,
						"sqrt": math.sqrt,
						"sin": math.sin,
						"cos": math.cos,
						"tan": math.tan,
						"asin": math.asin,
						"acos": math.acos,
						"atan": math.atan,
						"ln": math.log,
						"log": math.log10,
						"e ^": math.exp,
						"10 ^": lambda x: 10 ** x,
						}[t["OPERATOR"]](toNumber(t["NUM"]))

		return {
				"operator_add": bin_numeric_op(operator.add),
				"operator_subtract": bin_numeric_op(operator.sub),
				"operator_multiply": bin_numeric_op(operator.mul),
				"operator_divide": bin_numeric_op(operator.truediv),
				"operator_mod": bin_numeric_op(operator.mod),
				"operator_equals": bin_equality_op(operator.eq),
				"operator_gt": bin_equality_op(operator.gt),
				"operator_lt": bin_equality_op(operator.lt),
				"operator_and":	operator_and,
				"operator_or": operator_or,
				"operator_not": operator_not,
				"operator_length": operator_length,
				"operator_join": operator_join,
				"operator_contains": operator_contains,
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
				"stage_def": stage_def,
				"sprite_def": sprite_def,
				"program": program,
				"mathop": mathop,
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
