"""This module contains the class GrammarTransformer, which is used as a
transformer by the parser."""
from re import sub
from lark import Transformer


def expect_args(name, count, provided):
    """Raise an exception if count != provided."""
    if count != provided:
        raise Exception(f"{name} expected {count} arguments but {provided} were provided")


def expect_at_least_args(name, count, provided):
    """Raise an exception if count < provided."""
    if provided < count:
        raise Exception(f"{name} expected {count} or more arguments but {provided} were provided")


class ScratchTransformer(Transformer):  # pylint: disable=too-few-public-methods
    """This class is used as a transformer when parsing source code that will be
    compiled to scratch."""
    @staticmethod
    def _start(args):
        stage = [i for i in args if i["type"] == "stage_def"]
        if len(stage) > 1:
            raise Exception("stage defined multiple times")
        stage = stage[0] if stage else {"type": "stage_def", "procedures": []}
        stage["variables"] = [{
            "name": i["name"]
        } for i in args if i["type"] == "var_decl"]
        stage["lists"] = [{
            "name": i["name"]
        } for i in args if i["type"] == "arr_decl"]
        return {
            "type": "program",
            "stage": stage,
            "sprites": [i for i in args if i["type"] == "sprite_def"]
        }

    @staticmethod
    def _stage_def(args):
        costumes = [
            i for i in args
            if isinstance(i, dict) and i["type"] == "costume_list"
        ]
        if len(costumes) > 1:
            raise Exception("Stage has multiple costume lists")
        costumes = costumes[0]["costumes"] if costumes else []
        return {
            "type":
            "stage_def",
            "costumes":
            costumes,
            "procedures": [
                i for i in args
                if isinstance(i, dict) and i["type"] == "procedures_definition"
            ]
        }

    @staticmethod
    def _sprite_def(args):
        costumes = [
            i for i in args
            if isinstance(i, dict) and i["type"] == "costume_list"
        ]
        if len(costumes) > 1:
            raise Exception("Sprite has multiple costume lists")
        costumes = costumes[0]["costumes"] if costumes else []
        return {
            "type":
            "sprite_def",
            "name":
            args[0]["name"],
            "costumes":
            costumes,
            "variables": [{
                "name": i["name"]
            } for i in args if i["type"] == "var_decl"],
            "lists": [{
                "name": i["name"]
            } for i in args if i["type"] == "arr_decl"],
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
    def _block_stmt(args):
        return {"type": "block_stmt", "body": args[0]}

    @staticmethod
    def _proc_def_norm(args):
        return {
            "type": "procedures_definition",
            "name": args[0]["name"],
            "params": args[1]["params"],
            "warp": "false",
            "body": args[2]["body"]["stmts"]
        }

    @staticmethod
    def _proc_def_warp(args):
        return {
            "type": "procedures_definition",
            "name": args["name"],
            "params": args["params"],
            "warp": "true",
            "body": args["body"]
        }

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
        def unary_math_func(name, operator=None):
            def generated_func(node):
                expect_args(name, 1, len(node["args"]))
                return {
                    "type": "mathop",
                    "OPERATOR": operator or name,
                    "NUM": node["args"][0]
                }

            return generated_func

        def unknown_func(node):
            raise Exception(f"The function {node['name']} does not exist")

        def random(node):
            expect_args("random", 2, len(node["args"]))
            return {
                "type": "operator_random",
                "FROM": node["args"][0],
                "TO": node["args"][1]
            }

        def length(node):
            expect_args("length", 1, len(node["args"]))
            return {"type": "operator_length", "STRING": node["args"][0]}

        def join(node):
            expect_at_least_args("join", 2, len(node["args"]))
            def join_(args):
                return {
                    "type": "operator_join",
                    "STRING1": args[0],
                    "STRING2": args[1] if len(args) == 2 else join_(args[1:])
                }
            return join_(node["args"])

        def contains(node):
            expect_args("contains", 2, len(node["args"]))
            return {
                "type": "operator_contains",
                "STRING1": node["args"][0],
                "STRING2": node["args"][1]
            }

        def answer(node):
            expect_args("answer", 0, len(node["args"]))
            return {
                "type": "sensing_answer",
            }

        def timer(node):
            expect_args("timer", 0, len(node["args"]))
            return {
                "type": "sensing_timer",
            }

        def username(node):
            expect_args("username", 0, len(node["args"]))
            return {
                "type": "sensing_username",
            }

        def mousex(node):
            expect_args("mouseX", 0, len(node["args"]))
            return {
                "type": "sensing_mousex",
            }

        def mousey(node):
            expect_args("mouseY", 0, len(node["args"]))
            return {
                "type": "sensing_mousey",
            }


        def round_(node):
            expect_args("round", 1, len(node["args"]))
            return {
                "type": "operator_round",
                "NUM": node["args"][0]
            }

        call = {"name": args[0]["name"], "args": args[1]["args"]}

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
            "mouseX": mousex,
            "mouseY": mousey,
            "round": round_,
        }.get(call["name"], unknown_func)(call)

    @staticmethod
    def _procedures_call(args):
        def move_steps(node):
            expect_args("moveSteps", 1, len(node["args"]))
            return {"type": "motion_movesteps", "STEPS": node["args"][0]}

        def go_to_xy(node):
            expect_args("goToXY", 2, len(node["args"]))
            return {
                "type": "motion_gotoxy",
                "X": node["args"][0],
                "Y": node["args"][1]
            }

        def turn_right(node):
            expect_args("turnRight", 1, len(node["args"]))
            return {"type": "motion_turnright", "DEGREES": node["args"][0]}

        def turn_left(node):
            expect_args("turnLeft", 1, len(node["args"]))
            return {"type": "motion_turnleft", "DEGREES": node["args"][0]}

        def point_in_direction(node):
            expect_args("pointInDirection", 1, len(node["args"]))
            return {
                "type": "motion_pointindirection",
                "DIRECTION": node["args"][0]
            }

        def glide_secs_to_xy(node):
            expect_args("glideToXY", 3, len(node["args"]))
            return {
                "type": "motion_glidesecstoxy",
                "X": node["args"][0],
                "Y": node["args"][1],
                "SECS": node["args"][2]
            }

        def if_on_edge_bounce(node):
            expect_args("ifOnEdgeBounce", 0, len(node["args"]))
            return {"type": "motion_ifonedgebounce"}

        def wait(node):
            expect_args("wait", 1, len(node["args"]))
            return {"type": "control_wait", "DURATION": node["args"][0]}

        def wait_until(node):
            expect_args("waitUntil", 1, len(node["args"]))
            return {"type": "control_wait_until", "CONDITION": node["args"][0]}

        def say(node):
            expect_args("say", 1, len(node["args"]))
            return {"type": "looks_say", "MESSAGE": node["args"][0]}

        def say_seconds(node):
            expect_args("saySeconds", 2, len(node["args"]))
            return {
                "type": "looks_sayforsecs",
                "MESSAGE": node["args"][0],
                "SECS": node["args"][1]
            }

        def ask(node):
            expect_args("ask", 1, len(node["args"]))
            return {"type": "sensing_askandwait", "QUESTION": node["args"][0]}

        call = {
            "type": "procedures_call",
            "name": args[0]["name"],
            "args": args[1]["args"]
        }

        return {
            "moveSteps": move_steps,
            "goToXY": go_to_xy,
            "turnRight": turn_right,
            "turnLeft": turn_left,
            "pointInDirection": point_in_direction,
            "glideToXY": glide_secs_to_xy,
            "ifOnEdgeBounce": if_on_edge_bounce,
            "wait": wait,
            "waitUntil": wait_until,
            "say": say,
            "saySeconds": say_seconds,
            "ask": ask,
        }.get(call["name"], lambda x: x)(call)

    @staticmethod
    def _number(args):
        return float(args[0])

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
    def _arr_decl(args):
        return {"type": "arr_decl", "name": args[0]["name"]}

    @staticmethod
    def _arr_index(args):
        return {
            "type": "data_itemoflist",
            "name": args[0]["name"],
            "INDEX": args[1]
        }

    @staticmethod
    def _if_stmt(args):
        return {
            "type": "control_if",
            "CONDITION": args[0],
            "true_branch": args[1]["body"]["stmts"]
        }

    @staticmethod
    def _if_else_stmt(args):
        return {
            "type": "control_if_else",
            "CONDITION": args[0],
            "true_branch": args[1]["body"]["stmts"],
            "false_branch": args[2]["body"]["stmts"]
        }

    @staticmethod
    def _if_elif_stmt(args):
        return {
            "type": "control_if_else",
            "CONDITION": args[0],
            "true_branch": args[1]["body"]["stmts"],
            "false_branch": [args[2]]
        }

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
            "body": args[1]["body"]["stmts"]
        }

    @staticmethod
    def _while_loop(args):
        return {
            "type": "control_while",
            "CONDITION": args[0],
            "body": args[1]["body"]["stmts"]
        }

    @staticmethod
    def _repeat_loop(args):
        return {
            "type": "control_repeat",
            "TIMES": args[0],
            "body": args[1]["body"]["stmts"]
        }

    @staticmethod
    def _forever_loop(args):
        return {"type": "control_forever", "body": args[0]["body"]["stmts"]}

    @staticmethod
    def _true(_):
        return "true"

    @staticmethod
    def _false(_):
        return "false"
