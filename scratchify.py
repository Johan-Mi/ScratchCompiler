# Currently unused

def scratchify(tree):
	if type(tree) is dict:
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
				"func_call": basic_scratchify("args"),
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
