"""This module contains the optimize function, which optimizes an AST."""
import operator
import math
from cast import to_bool, to_number, to_string


def optimize(tree):
    """Returns an optimized version of an AST."""
    if isinstance(tree, dict):

        def basic_optimize(node, *args):
            for i in args:
                node[i] = optimize(node[i])

        def bin_numeric_op(func):
            def generated_func(node):
                basic_optimize(node, "NUM1", "NUM2")
                if isinstance(node["NUM1"], dict) \
                or isinstance(node["NUM2"], dict):
                    return node
                return func(to_number(node["NUM1"]), to_number(node["NUM2"]))

            return generated_func

        def bin_equality_op(func):
            def generated_func(node):
                basic_optimize(node, "OPERAND1", "OPERAND2")
                if isinstance(node["OPERAND1"], dict) \
                or isinstance(node["OPERAND2"], dict):
                    return node
                lhs = node["OPERAND1"]
                rhs = node["OPERAND2"]
                if type(rhs) is not type(lhs):
                    rhs = type(lhs)(rhs)
                return "true" if func(lhs, rhs) else "false"

            return generated_func

        def operator_and(node):
            basic_optimize(node, "OPERAND1", "OPERAND2")
            if isinstance(node["OPERAND1"], dict) \
            or isinstance(node["OPERAND2"], dict):
                return node
            return "true" \
                    if to_bool(node["OPERAND1"]) and to_bool(node["OPERAND2"]) \
                    else "false"

        def operator_or(node):
            basic_optimize(node, "OPERAND1", "OPERAND2")
            if isinstance(node["OPERAND1"], dict) \
            or isinstance(node["OPERAND2"], dict):
                return node
            return "true" \
                    if to_bool(node["OPERAND1"]) or to_bool(node["OPERAND2"]) \
                    else "false"

        def operator_not(node):
            basic_optimize(node, "OPERAND")
            if isinstance(node["OPERAND1"], dict):
                return node
            return "false" if to_bool(node["OPERAND"]) else "true"

        def operator_length(node):
            basic_optimize(node, "STRING")
            if isinstance(node["STRING"], dict):
                return node
            return len(to_string(node["STRING"]))

        def operator_join(node):
            basic_optimize(node, "STRING1", "STRING2")
            if isinstance(node["STRING1"], dict) \
            or isinstance(node["STRING2"], dict):
                return node
            return to_string(node["STRING1"]) + to_string(node["STRING2"])

        def operator_contains(node):
            basic_optimize(node, "STRING1", "STRING2")
            if isinstance(node["STRING1"], dict) \
            or isinstance(node["STRING2"], dict):
                return node
            return "true" if to_string(node["STRING2"]).lower() in \
                    to_string(node["STRING1"]).lower() else "false"

        def procedures_definition(node):
            basic_optimize(node, "body")
            return node

        def procedures_call(node):
            basic_optimize(node, "args")
            return node

        def control_if(node):
            basic_optimize(node, "CONDITION", "true_branch")
            if isinstance(node["CONDITION"], dict):
                return node
            return node["true_branch"] if to_bool(node["CONDITION"]) else None

        def control_if_else(node):
            basic_optimize(node, "CONDITION", "true_branch", "false_branch")
            if isinstance(node["CONDITION"], dict):
                return node
            return node["true_branch" if to_bool(node["CONDITION"]
                                                 ) else "false_branch"]

        def control_forever(node):
            basic_optimize(node, "body")
            return node

        def control_while(node):
            basic_optimize(node, "CONDITION", "body")
            if isinstance(node["CONDITION"], dict):
                return node
            return {
                "type": "control_forever",
                "body": node["body"]
            } if to_bool(node["CONDITION"]) else None

        def control_repeat_until(node):
            basic_optimize(node, "CONDITION", "body")
            if isinstance(node["CONDITION"], dict):
                return node
            return None if to_bool(node["CONDITION"]) \
                    else {
                        "type": "control_forever",
                        "body": node["body"]}

        def control_repeat(node):
            basic_optimize(node, "TIMES", "body")
            return node

        def data_setvariableto(node):
            basic_optimize(node, "value")
            return node

        def data_changevariableby(node):
            basic_optimize(node, "value")
            return node

        def stage_def(node):
            basic_optimize(node, "procedures")
            return node

        def sprite_def(node):
            basic_optimize(node, "procedures")
            return node

        def program(node):
            basic_optimize(node, "stage", "sprites")
            return node

        def mathop(node):
            basic_optimize(node, "NUM")
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

        return {
            "operator_add": bin_numeric_op(operator.add),
            "operator_subtract": bin_numeric_op(operator.sub),
            "operator_multiply": bin_numeric_op(operator.mul),
            "operator_divide": bin_numeric_op(operator.truediv),
            "operator_mod": bin_numeric_op(operator.mod),
            "operator_equals": bin_equality_op(operator.eq),
            "operator_gt": bin_equality_op(operator.gt),
            "operator_lt": bin_equality_op(operator.lt),
            "operator_and": operator_and,
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
    if isinstance(tree, list):
        force_list = lambda n: n if isinstance(n, list) else [n]
        return sum((force_list(optimize(i)) for i in tree), [])
    return tree
