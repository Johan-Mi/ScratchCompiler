from math import isnan

def toBool(v):
	if type(v) is bool:
		return v
	if type(v) is str:
		return v.lower() not in ("", "0", "false")
	return bool(v)

def toNumber(v):
	if type(v) in (int, float):
		return 0 if isnan(v) else v
	try:
		n = float(v)
		return 0 if isnan(n) else n
	except ValueError:
		return 0

def toString(v):
	return str(v)
