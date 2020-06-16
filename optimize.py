"""This module contains the optimize function, which optimizes an AST."""
import operator
import math
from cast import to_bool, to_number, to_string


def _basic_optimize(node, *args):
    for i in args:
        node[i] = optimize(node[i])


def _bin_numeric_op(func):
    def generated_func(node):
        _basic_optimize(node, "NUM1", "NUM2")
        if isinstance(node["NUM1"], dict) \
        or isinstance(node["NUM2"], dict):
            return node
        return func(to_number(node["NUM1"]), to_number(node["NUM2"]))

    return generated_func


def _bin_equality_op(func):
    def generated_func(node):
        _basic_optimize(node, "OPERAND1", "OPERAND2")
        if isinstance(node["OPERAND1"], dict) \
        or isinstance(node["OPERAND2"], dict):
            return node
        lhs = node["OPERAND1"]
        rhs = node["OPERAND2"]
        if type(rhs) is not type(lhs):
            rhs = type(lhs)(rhs)
        return "true" if func(lhs, rhs) else "false"

    return generated_func


def _operator_and(node):
    _basic_optimize(node, "OPERAND1", "OPERAND2")
    if isinstance(node["OPERAND1"], dict) \
    or isinstance(node["OPERAND2"], dict):
        return node
    return "true" \
            if to_bool(node["OPERAND1"]) and to_bool(node["OPERAND2"]) \
            else "false"


def _operator_or(node):
    _basic_optimize(node, "OPERAND1", "OPERAND2")
    if isinstance(node["OPERAND1"], dict) \
    or isinstance(node["OPERAND2"], dict):
        return node
    return "true" \
            if to_bool(node["OPERAND1"]) or to_bool(node["OPERAND2"]) \
            else "false"


def _operator_not(node):
    _basic_optimize(node, "OPERAND")
    if isinstance(node["OPERAND1"], dict):
        return node
    return "false" if to_bool(node["OPERAND"]) else "true"


def _operator_length(node):
    _basic_optimize(node, "STRING")
    if isinstance(node["STRING"], dict):
        return node
    return len(to_string(node["STRING"]))


def _operator_join(node):
    _basic_optimize(node, "STRING1", "STRING2")
    if isinstance(node["STRING1"], dict) \
    or isinstance(node["STRING2"], dict):
        return node
    return to_string(node["STRING1"]) + to_string(node["STRING2"])


def _operator_contains(node):
    _basic_optimize(node, "STRING1", "STRING2")
    if isinstance(node["STRING1"], dict) \
    or isinstance(node["STRING2"], dict):
        return node
    return "true" if to_string(node["STRING2"]).lower() in \
            to_string(node["STRING1"]).lower() else "false"


def _procedures_definition(node):
    _basic_optimize(node, "body")
    return node


def _procedures_call(node):
    _basic_optimize(node, "args")
    return node


def _control_if(node):
    _basic_optimize(node, "CONDITION", "true_branch")
    if isinstance(node["CONDITION"], dict):
        return node
    return node["true_branch"] if to_bool(node["CONDITION"]) else None


def _control_if_else(node):
    _basic_optimize(node, "CONDITION", "true_branch", "false_branch")
    if isinstance(node["CONDITION"], dict):
        return node
    return node["true_branch" if to_bool(node["CONDITION"]
                                         ) else "false_branch"]


def _control_forever(node):
    _basic_optimize(node, "body")
    return node


def _control_while(node):
    _basic_optimize(node, "CONDITION", "body")
    if isinstance(node["CONDITION"], dict):
        return node
    return {
        "type": "control_forever",
        "body": node["body"]
    } if to_bool(node["CONDITION"]) else None


def _control_repeat_until(node):
    _basic_optimize(node, "CONDITION", "body")
    if isinstance(node["CONDITION"], dict):
        return node
    return None if to_bool(node["CONDITION"]) \
            else {
                "type": "control_forever",
                "body": node["body"]}


def _control_repeat(node):
    _basic_optimize(node, "TIMES", "body")
    return node


def _data_setvariableto(node):
    _basic_optimize(node, "value")
    return node


def _data_changevariableby(node):
    _basic_optimize(node, "value")
    return node


def _data_addtolist(node):
    _basic_optimize(node, "value")
    return node


def _data_itemoflist(node):
    _basic_optimize(node, "INDEX")
    return node


def _stage_def(node):
    _basic_optimize(node, "procedures")
    return node


def _sprite_def(node):
    _basic_optimize(node, "procedures")
    return node


def _program(node):
    _basic_optimize(node, "stage", "sprites")
    return node


def _mathop(node):
    _basic_optimize(node, "NUM")
    if isinstance(node["NUM"], dict):
        return node
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
        "10 ^": lambda x: 10**x,
    }[node["OPERATOR"]](to_number(node["NUM"]))


def _control_wait(node):
    _basic_optimize(node, "DURATION")
    return node


def _control_wait_until(node):
    _basic_optimize(node, "CONDITION")
    return node


def _looks_say(node):
    _basic_optimize(node, "MESSAGE")
    return node


def _looks_sayforsecs(node):
    _basic_optimize(node, "MESSAGE", "SECS")
    return node


def _sensing_askandwait(node):
    _basic_optimize(node, "QUESTION")
    return node


def optimize(tree):
    """Returns an optimized version of an AST."""
    if isinstance(tree, dict):
        return {
            "operator_add": _bin_numeric_op(operator.add),
            "operator_subtract": _bin_numeric_op(operator.sub),
            "operator_multiply": _bin_numeric_op(operator.mul),
            "operator_divide": _bin_numeric_op(operator.truediv),
            "operator_mod": _bin_numeric_op(operator.mod),
            "operator_equals": _bin_equality_op(operator.eq),
            "operator_gt": _bin_equality_op(operator.gt),
            "operator_lt": _bin_equality_op(operator.lt),
            "operator_and": _operator_and,
            "operator_or": _operator_or,
            "operator_not": _operator_not,
            "operator_length": _operator_length,
            "operator_join": _operator_join,
            "operator_contains": _operator_contains,
            "procedures_definition": _procedures_definition,
            "procedures_call": _procedures_call,
            "control_if": _control_if,
            "control_if_else": _control_if_else,
            "control_forever": _control_forever,
            "control_while": _control_while,
            "control_repeat_until": _control_repeat_until,
            "control_repeat": _control_repeat,
            "control_wait": _control_wait,
            "control_wait_until": _control_wait_until,
            "data_setvariableto": _data_setvariableto,
            "data_changevariableby": _data_changevariableby,
            "data_addtolist": _data_addtolist,
            "data_itemoflist": _data_itemoflist,
            "stage_def": _stage_def,
            "sprite_def": _sprite_def,
            "program": _program,
            "mathop": _mathop,
            "looks_say": _looks_say,
            "looks_sayforsecs": _looks_sayforsecs,
            "sensing_askandwait": _sensing_askandwait,
        }.get(tree["type"], lambda x: x)(tree)
    if isinstance(tree, list):
        force_list = lambda n: n if isinstance(n, list) else [n]
        return sum((force_list(optimize(i)) for i in tree), [])
    return tree
