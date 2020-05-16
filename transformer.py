from lark import Transformer

class GrammarTransformer(Transformer):
	def ident(args):
		return {"type": "ident",
				"name": str(args[0])}
	def func_def(args):
		return {"type": "func_def",
				"name": args[0]["name"],
				"params": args[1]["params"],
				"body": args[2]["body"]["stmts"]}
	def param_list(args):
		return {"type": "param_list",
				"params": [{"type": "param", "name": p["name"]} for p in args]}
	def func_call(args):
		return {"type": "func_call",
				"name": args[0]["name"],
				"args": args[1]["args"]}
	def number(args):
		return {"type": "number",
				"num": float(args[0])}
	def block_stmt(args):
		return {"type": "block_stmt",
				"body": args[0]}
	def stmts(args):
		return {"type": "stmts",
				"stmts": args}
	def arg_list(args):
		return {"type": "arg_list",
				"args": args}
	def addition(args):
		return {"type": "addition",
				"lhs": args[0],
				"rhs": args[1]}
	def subtraction(args):
		return {"type": "subtraction",
				"lhs": args[0],
				"rhs": args[1]}
	def multiplication(args):
		return {"type": "multiplication",
				"lhs": args[0],
				"rhs": args[1]}
	def division(args):
		return {"type": "division",
				"lhs": args[0],
				"rhs": args[1]}
	def modulo(args):
		return {"type": "modulo",
				"lhs": args[0],
				"rhs": args[1]}
	def start(args):
		return args
