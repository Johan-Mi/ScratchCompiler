"""This module contains the class ScratchTransformer, which is used as a
transformer by the parser."""
from re import sub
from lark import Transformer


def expect_at_least_args(name, count, provided):
    """Raise an exception if count < provided."""
    if provided < count:
        raise TypeError(f"{name} expected {count} or more arguments but \
{provided} were provided")


class ScratchTransformer(Transformer):  # pylint: disable=too-few-public-methods
    """This class is used as a transformer when parsing source code that will be
    compiled to scratch."""
    @staticmethod
    def _start(args):
        stages = [i for i in args if i["type"] == "stage_def"]
        if len(stages) > 1:
            raise Exception("Stage defined multiple times")

        return {
            "type": "program",
            "stage": {
                "type":
                "stage_def",
                "costumes":
                stages[0]["costumes"] if stages else [],
                "procedures":
                stages[0]["procedures"] if stages else [],
                "variables": [{
                    "name": i["name"]
                } for i in args if i["type"] == "var_decl"],
                "lists": [{
                    "name": i["name"]
                } for i in args if i["type"] == "list_decl"]
            },
            "sprites": [i for i in args if i["type"] == "sprite_def"]
        }

    @staticmethod
    def _stage_def(args):
        costume_lists = [
            i for i in args
            if isinstance(i, dict) and i["type"] == "costume_list"
        ]
        if len(costume_lists) > 1:
            raise Exception("Stage has multiple costume lists")
        return {
            "type":
            "stage_def",
            "costumes":
            costume_lists[0]["costumes"] if costume_lists else [],
            "procedures": [
                i for i in args
                if isinstance(i, dict) and i["type"] == "procedures_definition"
            ]
        }

    @staticmethod
    def _sprite_def(args):
        costume_lists = [
            i for i in args
            if isinstance(i, dict) and i["type"] == "costume_list"
        ]
        if len(costume_lists) > 1:
            raise Exception("Sprite has multiple costume lists")
        return {
            "type":
            "sprite_def",
            "name":
            args[0]["name"],
            "costumes":
            costume_lists[0]["costumes"] if costume_lists else [],
            "variables": [{
                "name": i["name"]
            } for i in args if i["type"] == "var_decl"],
            "lists": [{
                "name": i["name"]
            } for i in args if i["type"] == "list_decl"],
            "procedures":
            [i for i in args if i["type"] == "procedures_definition"]
        }

    @staticmethod
    def _costume_list(args):
        return {"type": "costume_list", "costumes": args}

    @staticmethod
    def _ident(args):
        return {"type": "ident", "name": str(args[0])}

    @staticmethod
    def _stmts(args):
        return {"type": "stmts", "stmts": args}

    @staticmethod
    def _proc_def_norm(args):
        return {
            "type": "procedures_definition",
            "name": args[0]["name"],
            "params": args[1]["params"],
            "warp": "false",
            "body": args[2]["stmts"]
        }

    @staticmethod
    def _proc_def_warp(args):
        return {**args[0], "warp": "true"}

    @staticmethod
    def _param_list(args):
        return {
            "type": "param_list",
            "params": [{
                "type": "param",
                "name": p["name"]
            } for p in args]
        }

    @staticmethod
    def _func_call(args):
        call = {"name": args[0]["name"], "args": args[1]["args"]}

        def expect_args(count):
            if count != len(call["args"]):
                raise TypeError(f"Function {call['name']}() expected {count} \
arguments but {len(call['args'])} were provided")

        def unary_math_func(name, operator=None):
            def generated_func(node):
                expect_args(1)
                return {
                    "type": "mathop",
                    "OPERATOR": operator or name,
                    "NUM": node["args"][0]
                }

            return generated_func

        def unknown_func(node):
            raise Exception(f"The function {node['name']} does not exist")

        def random(node):
            expect_args(2)
            return {
                "type": "operator_random",
                "FROM": node["args"][0],
                "TO": node["args"][1]
            }

        def length(node):
            expect_args(1)
            return {"type": "operator_length", "STRING": node["args"][0]}

        def join(node):
            expect_at_least_args("join", 2, len(node["args"]))

            def join_(args):
                if len(args) == 1:
                    return args[0]
                return {
                    "type": "operator_join",
                    "STRING1": join_(args[:len(args) // 2]),
                    "STRING2": join_(args[len(args) // 2:])
                }

            return join_(node["args"])

        def contains(node):
            expect_args(2)
            return {
                "type": "operator_contains",
                "STRING1": node["args"][0],
                "STRING2": node["args"][1]
            }

        def answer(_):
            expect_args(0)
            return {
                "type": "sensing_answer",
            }

        def timer(_):
            expect_args(0)
            return {
                "type": "sensing_timer",
            }

        def username(_):
            expect_args(0)
            return {
                "type": "sensing_username",
            }

        def mousex(_):
            expect_args(0)
            return {
                "type": "sensing_mousex",
            }

        def mousey(_):
            expect_args(0)
            return {
                "type": "sensing_mousey",
            }

        def round_(node):
            expect_args(1)
            return {"type": "operator_round", "NUM": node["args"][0]}

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
            "exp": unary_math_func("exp", "e ^"),
            "pow": unary_math_func("pow", "10 ^"),
            "random": random,
            "join": join,
            "contains": contains,
            "length": length,
            "answer": answer,
            "timer": timer,
            "username": username,
            "mouse_x": mousex,
            "mouse_y": mousey,
            "round": round_,
        }.get(call["name"], unknown_func)(call)

    @staticmethod
    def _procedures_call(args):
        call = {
            "type": "procedures_call",
            "name": args[0]["name"],
            "args": args[1]["args"]
        }

        def expect_args(count):
            if count != len(call["args"]):
                raise TypeError(f"Procedure {call['name']}() expected {count} \
arguments but {len(call['args'])} were provided")

        def move_steps(node):
            expect_args(1)
            return {"type": "motion_movesteps", "STEPS": node["args"][0]}

        def go_to_xy(node):
            expect_args(2)
            return {
                "type": "motion_gotoxy",
                "X": node["args"][0],
                "Y": node["args"][1]
            }

        def turn_right(node):
            expect_args(1)
            return {"type": "motion_turnright", "DEGREES": node["args"][0]}

        def turn_left(node):
            expect_args(1)
            return {"type": "motion_turnleft", "DEGREES": node["args"][0]}

        def point_in_direction(node):
            expect_args(1)
            return {
                "type": "motion_pointindirection",
                "DIRECTION": node["args"][0]
            }

        def glide_secs_to_xy(node):
            expect_args(3)
            return {
                "type": "motion_glidesecstoxy",
                "X": node["args"][0],
                "Y": node["args"][1],
                "SECS": node["args"][2]
            }

        def if_on_edge_bounce(_):
            expect_args(0)
            return {"type": "motion_ifonedgebounce"}

        def wait(node):
            expect_args(1)
            return {"type": "control_wait", "DURATION": node["args"][0]}

        def wait_until(node):
            expect_args(1)
            return {"type": "control_wait_until", "CONDITION": node["args"][0]}

        def say(node):
            expect_args(1)
            return {"type": "looks_say", "MESSAGE": node["args"][0]}

        def say_seconds(node):
            expect_args(2)
            return {
                "type": "looks_sayforsecs",
                "MESSAGE": node["args"][0],
                "SECS": node["args"][1]
            }

        def ask(node):
            expect_args(1)
            return {"type": "sensing_askandwait", "QUESTION": node["args"][0]}

        def pen_down(_):
            expect_args(0)
            return {"type": "pen_pendown"}

        def pen_up(_):
            expect_args(0)
            return {"type": "pen_penup"}

        def stamp(_):
            expect_args(0)
            return {"type": "pen_stamp"}

        def erase_all(_):
            expect_args(0)
            return {"type": "pen_eraseall"}

        return {
            "move_steps": move_steps,
            "go_to_xy": go_to_xy,
            "turn_right": turn_right,
            "turn_left": turn_left,
            "point_in_direction": point_in_direction,
            "glide_to_xy": glide_secs_to_xy,
            "if_on_edge_bounce": if_on_edge_bounce,
            "wait": wait,
            "wait_until": wait_until,
            "say": say,
            "say_for_seconds": say_seconds,
            "ask": ask,
            "pen_down": pen_down,
            "pen_up": pen_up,
            "stamp": stamp,
            "erase_all": erase_all,
        }.get(call["name"], lambda x: x)(call)

    @staticmethod
    def _member_func_call(args):
        return {
            "type": "member_func_call",
            "caller": args[0]["name"],
            "name": args[1]["name"],
            "args": args[2]["args"],
        }

    @staticmethod
    def _member_proc_call(args):
        return {
            "type": "member_proc_call",
            "caller": args[0]["name"],
            "name": args[1]["name"],
            "args": args[2]["args"],
        }

    @staticmethod
    def _number(args):
        float_val = float(args[0])
        int_val = int(args[0])
        return int_val if int_val == float_val else float_val

    @staticmethod
    def _string(args):
        return sub(r"\\([\\\"])", r"\1", args[0][1:-1])

    @staticmethod
    def _arg_list(args):
        return {"type": "arg_list", "args": args}

    @staticmethod
    def _addition(args):
        return {"type": "operator_add", "NUM1": args[0], "NUM2": args[1]}

    @staticmethod
    def _subtraction(args):
        return {"type": "operator_subtract", "NUM1": args[0], "NUM2": args[1]}

    @staticmethod
    def _multiplication(args):
        return {"type": "operator_multiply", "NUM1": args[0], "NUM2": args[1]}

    @staticmethod
    def _division(args):
        return {"type": "operator_divide", "NUM1": args[0], "NUM2": args[1]}

    @staticmethod
    def _modulo(args):
        return {"type": "operator_mod", "NUM1": args[0], "NUM2": args[1]}

    @staticmethod
    def _negate(args):
        return {"type": "operator_subtract", "NUM1": 0.0, "NUM2": args[0]}

    @staticmethod
    def _less_than(args):
        return {
            "type": "operator_lt",
            "OPERAND1": args[0],
            "OPERAND2": args[1]
        }

    @staticmethod
    def _greater_than(args):
        return {
            "type": "operator_gt",
            "OPERAND1": args[0],
            "OPERAND2": args[1]
        }

    @staticmethod
    def _equal_to(args):
        return {
            "type": "operator_equals",
            "OPERAND1": args[0],
            "OPERAND2": args[1]
        }

    @staticmethod
    def _logical_or(args):
        return {
            "type": "operator_or",
            "OPERAND1": args[0],
            "OPERAND2": args[1]
        }

    @staticmethod
    def _logical_and(args):
        return {
            "type": "operator_and",
            "OPERAND1": args[0],
            "OPERAND2": args[1]
        }

    @staticmethod
    def _logical_not(args):
        return {"type": "operator_not", "OPERAND": args[0]}

    @staticmethod
    def _var_decl(args):
        return {"type": "var_decl", "name": args[0]["name"]}

    @staticmethod
    def _list_decl(args):
        return {"type": "list_decl", "name": args[0]["name"]}

    @staticmethod
    def _list_index(args):
        return {
            "type": "data_itemoflist",
            "name": args[0]["name"],
            "INDEX": args[1]
        }

    @staticmethod
    def _if_stmt(args):
        def if_stmt(args):
            if len(args) == 2:
                return {
                    "type": "control_if",
                    "CONDITION": args[0],
                    "true_branch": args[1]["stmts"]
                }
            if len(args) == 3:
                return {
                    "type": "control_if_else",
                    "CONDITION": args[0],
                    "true_branch": args[1]["stmts"],
                    "false_branch": args[2]["stmts"]
                }
            return {
                "type": "control_if_else",
                "CONDITION": args[0],
                "true_branch": args[1]["stmts"],
                "false_branch": if_stmt(args[2:])
            }

        return if_stmt(args)

    @staticmethod
    def _var_eq(args):
        return {
            "type": "data_setvariableto",
            "name": args[0]["name"],
            "value": args[1]
        }

    @staticmethod
    def _var_peq(args):
        return {
            "type": "data_changevariableby",
            "name": args[0]["name"],
            "value": args[1]
        }

    @staticmethod
    def _var_meq(args):
        return {
            "type": "data_changevariableby",
            "name": args[0]["name"],
            "value": {
                "type": "operator_subtract",
                "NUM1": 0.0,
                "NUM2": args[1]
            }
        }

    @staticmethod
    def _var_teq(args):
        return {
            "type": "data_setvariableto",
            "name": args[0]["name"],
            "value": {
                "type": "operator_multiply",
                "NUM1": args[0],
                "NUM2": args[1]
            }
        }

    @staticmethod
    def _var_deq(args):
        return {
            "type": "data_setvariableto",
            "name": args[0]["name"],
            "value": {
                "type": "operator_divide",
                "NUM1": args[0],
                "NUM2": args[1]
            }
        }

    @staticmethod
    def _until_loop(args):
        return {
            "type": "control_repeat_until",
            "CONDITION": args[0],
            "body": args[1]["stmts"]
        }

    @staticmethod
    def _while_loop(args):
        return {
            "type": "control_while",
            "CONDITION": args[0],
            "body": args[1]["stmts"]
        }

    @staticmethod
    def _repeat_loop(args):
        return {
            "type": "control_repeat",
            "TIMES": args[0],
            "body": args[1]["stmts"]
        }

    @staticmethod
    def _forever_loop(args):
        return {"type": "control_forever", "body": args[0]["stmts"]}

    @staticmethod
    def _true(_):
        return "true"

    @staticmethod
    def _false(_):
        return "false"
