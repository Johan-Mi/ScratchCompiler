"""This module contains the scratchify function, which converts an AST into a
valid object for the project.json file in a scratch project."""
import itertools
from resolve import resolve_var, resolve_list, resolve_proc, \
resolve_var_or_list, resolve_ident

id_maker = (f"_{i}" for i in itertools.count())


def _assign_parent(parent_id: str, *args):
    for i in args:
        if isinstance(i[0], tuple):
            i[0][1]["parent"] = parent_id


def _doubly_link_stmts(first: tuple, rest: list):
    if len(rest) > 0:
        rest[0][0][1]["parent"] = first[0]
        for i in range(len(rest) - 1):
            rest[i][0][1]["next"] = rest[i + 1][0][0]
            rest[i + 1][0][1]["parent"] = rest[i][0][0]


def _block_noargs(opcode):
    def generated_func(node: dict, env):
        return [(node["id"], {
            "opcode": opcode,
            "next": None,
            "parent": None,
            "inputs": {},
            "fields": {},
            "shadow": False,
            "topLevel": False
        })]

    return generated_func


def _number_input(nodes) -> list:
    if nodes[0][0][0] in (12, 13):
        return [3, nodes[0][0], [4, 0]]
    return [1, nodes[0][0]]


def _stage_def(node: dict, env):
    return {
        "isStage":
        True,
        "name":
        "Stage",
        "variables":
        {var["id"]: [var["name"], 0]
         for var in node["variables"]},
        "lists": {lst["id"]: [lst["name"], []]
                  for lst in node["lists"]},
        "broadcasts": {},
        "blocks":
        dict(i
             for i in sum((scratchify(i, env) for i in node["procedures"]), [])
             if isinstance(i, tuple)),
        "comments": {},
        "currentCostume":
        0,
        "costumes": [],
        "sounds": [],
        "volume":
        0,
        "layerOrder":
        0,
        "tempo":
        0,
        "videoTransparency":
        0,
        "videoState":
        "off"
    }


def _sprite_def(node: dict, env):
    return {
        "isStage":
        False,
        "name":
        node["name"],
        "variables":
        {var["id"]: [var["name"], 0]
         for var in node["variables"]},
        "lists": {lst["id"]: [lst["name"], []]
                  for lst in node["lists"]},
        "broadcasts": {},
        "blocks":
        dict(block for block in sum((scratchify(proc, env)
                                     for proc in node["procedures"]), [])
             if isinstance(block, tuple)),
        "comments": {},
        "currentCostume":
        0,
        "costumes": [],
        "sounds": [],
        "volume":
        0,
        "layerOrder":
        env["index"] + 1,
        "visible":
        True,
        "x":
        0,
        "y":
        0,
        "size":
        100,
        "direction":
        90,
        "draggable":
        False,
        "rotationStyle":
        "all around"
    }


def _procedures_definition(node: dict, env) -> list:
    params = [scratchify(i, env)[0] for i in node["params"]]

    body = [scratchify(i, env) for i in node["body"]]

    definition = (node["id"], {
        "opcode": "procedures_definition",
        "next": body[0][0][0] if len(body) > 0 else None,
        "parent": None,
        "inputs": {
            "custom_block": [1, next(id_maker)]
        },
        "fields": {},
        "shadow": False,
        "topLevel": True,
        "x": 0,
        "y": 0
    })

    prototype_inputs = {next(id_maker): [1, i[0]] for i in params}

    prototype = (definition[1]["inputs"]["custom_block"][1], {
        "opcode": "procedures_prototype",
        "next": None,
        "parent": definition[0],
        "inputs": prototype_inputs,
        "fields": {},
        "shadow": True,
        "topLevel": False,
        "mutation": {
            "tagName":
            "mutation",
            "children": [],
            "proccode":
            node["name"] + " %s" * len(params),
            "argumentids":
            str(list(prototype_inputs)).replace("'", "\""),
            "argumentnames":
            str([i["name"] for i in node["params"]]).replace("'", "\""),
            "argumentdefaults":
            str([""] * len(params)).replace("'", "\""),
            "warp":
            node["warp"]
        }
    })

    for i in params:
        i[1]["parent"] = prototype[0]

    _doubly_link_stmts(definition, body)

    node["prototype"] = prototype

    return sum(body, [*params, definition, prototype])


def _param(node: dict, _) -> list:
    return [(node["id"], {
        "opcode": "argument_reporter_string_number",
        "next": None,
        "parent": None,
        "inputs": {},
        "fields": {
            "VALUE": [node["name"], None]
        },
        "shadow": False,
        "topLevel": False
    })]


def _motion_movesteps(node: dict, env) -> list:
    steps = scratchify(node["STEPS"], env)
    _assign_parent(node["id"], steps)
    return [(node["id"], {
        "opcode": "motion_movesteps",
        "next": None,
        "parent": None,
        "inputs": {
            "STEPS": _number_input(steps),
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + steps


def _motion_gotoxy(node: dict, env) -> list:
    x_coord = scratchify(node["X"], env)
    y_coord = scratchify(node["Y"], env)
    _assign_parent(node["id"], x_coord, y_coord)
    return [(node["id"], {
        "opcode": "motion_gotoxy",
        "next": None,
        "parent": None,
        "inputs": {
            "X": _number_input(x_coord),
            "Y": _number_input(y_coord)
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + x_coord + y_coord


def _motion_turnright(node: dict, env) -> dict:
    degrees = scratchify(node["DEGREES"], env)
    _assign_parent(node["id"], degrees)
    return [(node["id"], {
        "opcode": "motion_turnright",
        "next": None,
        "parent": None,
        "inputs": {
            "DEGREES": _number_input(degrees)
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + degrees


def _motion_turnleft(node: dict, env) -> dict:
    degrees = scratchify(node["DEGREES"], env)
    _assign_parent(node["id"], degrees)
    return [(node["id"], {
        "opcode": "motion_turnleft",
        "next": None,
        "parent": None,
        "inputs": {
            "DEGREES": _number_input(degrees)
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + degrees


def _motion_pointindirection(node: dict, env) -> list:
    direction = scratchify(node["DIRECTION"], env)
    _assign_parent(node["id"], direction)
    return [(node["id"], {
        "opcode": "motion_pointindirection",
        "next": None,
        "parent": None,
        "inputs": {
            "DIRECTION": _number_input(direction)
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + direction


def _motion_glidesecstoxy(node: dict, env) -> list:
    x_coord = scratchify(node["X"], env)
    y_coord = scratchify(node["Y"], env)
    secs = scratchify(node["SECS"], env)
    _assign_parent(node["id"], x_coord, y_coord, secs)
    return [(node["id"], {
        "opcode": "motion_glidesecstoxy",
        "next": None,
        "parent": None,
        "inputs": {
            "X": _number_input(x_coord),
            "Y": _number_input(y_coord),
            "SECS": _number_input(secs)
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + x_coord + y_coord + secs


def _control_if(node: dict, env) -> list:
    condition = scratchify(node["CONDITION"], env)
    _assign_parent(node["id"], condition)

    substack = [scratchify(i, env) for i in node["true_branch"]]

    if_stmt = (node["id"], {
        "opcode": "control_if",
        "next": None,
        "parent": None,
        "inputs": {
            "CONDITION": [2, condition[0][0]],
            "SUBSTACK": [2, substack[0][0][0]]
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })

    _doubly_link_stmts(if_stmt, substack)

    return sum(substack, [if_stmt] + condition)


def _control_if_else(node: dict, env) -> list:
    condition = scratchify(node["CONDITION"], env)
    _assign_parent(node["id"], condition)

    substack = [scratchify(i, env) for i in node["true_branch"]]
    substack2 = [scratchify(i, env) for i in node["false_branch"]]

    if_stmt = (node["id"], {
        "opcode": "control_if_else",
        "next": None,
        "parent": None,
        "inputs": {
            "CONDITION": [2, condition[0][0]],
            "SUBSTACK": [2, substack[0][0][0]],
            "SUBSTACK2": [2, substack2[0][0][0]]
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })

    _doubly_link_stmts(if_stmt, substack)
    _doubly_link_stmts(if_stmt, substack2)

    return sum(substack + substack2, [if_stmt, *condition])


def _control_repeat(node: dict, env) -> list:
    times = scratchify(node["TIMES"], env)
    _assign_parent(node["id"], times)

    substack = [scratchify(i, env) for i in node["body"]]

    loop = (node["id"], {
        "opcode": "control_repeat",
        "next": None,
        "parent": None,
        "inputs": {
            "TIMES": _number_input(times),
            "SUBSTACK": [2, substack[0][0][0]]
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })

    _doubly_link_stmts(loop, substack)

    return sum(substack, [loop, *times])


def _control_forever(node: dict, env) -> list:
    substack = [scratchify(i, env) for i in node["body"]]

    loop = (node["id"], {
        "opcode": "control_forever",
        "next": None,
        "parent": None,
        "inputs": {
            "SUBSTACK": [2, substack[0][0][0]]
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })

    _doubly_link_stmts(loop, substack)

    return sum(substack, [loop])


def _control_while(node: dict, env) -> list:
    condition = scratchify(node["CONDITION"], env)
    _assign_parent(node["id"], condition)

    substack = [scratchify(i, env) for i in node["body"]]

    loop = (node["id"], {
        "opcode": "control_while",
        "next": None,
        "parent": None,
        "inputs": {
            "CONDITION": [2, condition[0][0]],
            "SUBSTACK": [2, substack[0][0][0]]
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })

    _doubly_link_stmts(loop, substack)

    return sum(substack, [loop, *condition])


def _control_repeat_until(node: dict, env) -> list:
    condition = scratchify(node["CONDITION"], env)
    _assign_parent(node["id"], condition)

    substack = [scratchify(i, env) for i in node["body"]]

    loop = (node["id"], {
        "opcode": "control_repeat_until",
        "next": None,
        "parent": None,
        "inputs": {
            "CONDITION": [2, condition[0][0]],
            "SUBSTACK": [2, substack[0][0][0]]
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })

    _doubly_link_stmts(loop, substack)

    return sum(substack, [loop, *condition])


def _bin_numeric_op(opcode: str):
    def generated_func(node: dict, env):
        num1 = scratchify(node["NUM1"], env)
        num2 = scratchify(node["NUM2"], env)
        _assign_parent(node["id"], num1, num2)
        return [(node["id"], {
            "opcode": opcode,
            "next": None,
            "parent": None,
            "inputs": {
                "NUM1": _number_input(num1),
                "NUM2": _number_input(num2)
            },
            "fields": {},
            "shadow": False,
            "topLevel": False
        })] + num1 + num2

    return generated_func


def _binary_logic_operator(opcode: str):
    def generated_func(node: dict, env):
        operand1 = scratchify(node["OPERAND1"], env)
        operand2 = scratchify(node["OPERAND2"], env)
        _assign_parent(node["id"], operand1, operand2)
        return [(node["id"], {
            "opcode": opcode,
            "next": None,
            "parent": None,
            "inputs": {
                "OPERAND1": _number_input(operand1),
                "OPERAND2": _number_input(operand2)
            },
            "fields": {},
            "shadow": False,
            "topLevel": False
        })] + operand1 + operand2

    return generated_func


def _operator_not(node: dict, env) -> list:
    operand = scratchify(node["OPERAND"], env)
    _assign_parent(node["id"], operand)
    return [(node["id"], {
        "opcode": "operator_not",
        "next": None,
        "parent": None,
        "inputs": {
            "OPERAND": _number_input(operand)
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + operand


def _operator_random(node: dict, env) -> list:
    low = scratchify(node["FROM"], env)
    high = scratchify(node["TO"], env)
    _assign_parent(node["id"], low, high)
    return [(node["id"], {
        "opcode": "operator_random",
        "next": None,
        "parent": None,
        "inputs": {
            "FROM": _number_input(low),
            "TO": _number_input(high)
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + low + high


def _operator_join(node: dict, env) -> list:
    string1 = scratchify(node["STRING1"], env)
    string2 = scratchify(node["STRING2"], env)
    _assign_parent(node["id"], string1, string2)
    return [(node["id"], {
        "opcode": "operator_join",
        "next": None,
        "parent": None,
        "inputs": {
            "STRING1": _number_input(string1),
            "STRING2": _number_input(string2)
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + string1 + string2


def _data_setvariableto(node: dict, env) -> list:
    var_id = resolve_var(node["name"], env)
    value = scratchify(node["value"], env)
    _assign_parent(node["id"], value)
    return [(node["id"], {
        "opcode": "data_setvariableto",
        "next": None,
        "parent": None,
        "inputs": {
            "VALUE": _number_input(value)
        },
        "fields": {
            "VARIABLE": [node["name"], var_id]
        },
        "shadow": False,
        "topLevel": False
    })] + value


def _data_changevariableby(node: dict, env) -> list:
    var_or_list, var_id = resolve_var_or_list(node["name"], env)
    value = scratchify(node["value"], env)
    _assign_parent(node["id"], value)
    if var_or_list == "var":
        return [(node["id"], {
            "opcode": "data_changevariableby",
            "next": None,
            "parent": None,
            "inputs": {
                "VALUE": _number_input(value)
            },
            "fields": {
                "VARIABLE": [node["name"], var_id]
            },
            "shadow": False,
            "topLevel": False
        })] + value
    return [(node["id"], {
        "opcode": "data_addtolist",
        "next": None,
        "parent": None,
        "inputs": {
            "ITEM": _number_input(value)
        },
        "fields": {
            "LIST": [node["name"], var_id]
        },
        "shadow": False,
        "topLevel": False
    })] + value


def _data_itemoflist(node: dict, env) -> list:
    list_id = resolve_list(node["name"], env)
    index = scratchify(node["INDEX"], env)
    _assign_parent(node["id"], index)
    return [(node["id"], {
        "opcode": "data_itemoflist",
        "next": None,
        "parent": None,
        "inputs": {
            "INDEX": _number_input(index)
        },
        "fields": {
            "LIST": [node["name"], list_id]
        },
        "shadow": False,
        "topLevel": False
    })] + index


def _procedures_call(node: dict, env) -> list:
    proc = resolve_proc(node["name"], env)
    args = [scratchify(i, env) for i in node["args"]]
    _assign_parent(node["id"], *args)
    call = [(node["id"], {
        "opcode": "procedures_call",
        "next": None,
        "parent": None,
        "inputs": {
            i: _number_input(j)
            for i, j in zip(proc["prototype"][1]["inputs"], args)},
        "fields": {},
        "shadow": False,
        "topLevel": False,
        "mutation": {
            "tagName": "mutation",
            "children": [],
            "proccode": node["name"] + " %s" * len(proc["params"]),
            "argumentids": str(proc["prototype"][1]["inputs"]) \
                    .replace("'", "\""),
            "warp": proc["warp"]}})]
    return sum(args, call)


def _ident(node: dict, env) -> list:
    var_or_list, var_id = resolve_var_or_list(node["name"], env)
    return [[[12 if var_or_list == "var" else 13, node["name"], var_id]]]


def _control_wait(node: dict, env) -> list:
    duration = scratchify(node["DURATION"], env)
    _assign_parent(node["id"], duration)
    return [(node["id"], {
        "opcode": "control_wait",
        "next": None,
        "parent": None,
        "inputs": {
            "DURATION": _number_input(duration)
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + duration


def _control_wait_until(node: dict, env) -> list:
    condition = scratchify(node["CONDITION"], env)
    _assign_parent(node["id"], condition)
    return [(node["id"], {
        "opcode": "control_wait_until",
        "next": None,
        "parent": None,
        "inputs": {
            "CONDITION": _number_input(condition)
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + condition


def _looks_say(node: dict, env) -> list:
    message = scratchify(node["MESSAGE"], env)
    _assign_parent(node["id"], message)
    return [(node["id"], {
        "opcode": "looks_say",
        "next": None,
        "parent": None,
        "inputs": {
            "MESSAGE": _number_input(message)
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + message


def _looks_sayforsecs(node: dict, env) -> list:
    message = scratchify(node["MESSAGE"], env)
    secs = scratchify(node["SECS"], env)
    _assign_parent(node["id"], message, secs)
    return [(node["id"], {
        "opcode": "looks_sayforsecs",
        "next": None,
        "parent": None,
        "inputs": {
            "MESSAGE": _number_input(message),
            "SECS": _number_input(secs)
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + message + secs


def _sensing_askandwait(node: dict, env) -> list:
    question = scratchify(node["QUESTION"], env)
    _assign_parent(node["id"], question)
    return [(node["id"], {
        "opcode": "sensing_askandwait",
        "next": None,
        "parent": None,
        "inputs": {
            "QUESTION": _number_input(question),
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + question


def _operator_round(node: dict, env) -> list:
    num = scratchify(node["NUM"], env)
    _assign_parent(node["id"], num)
    return [(node["id"], {
        "opcode": "operator_round",
        "next": None,
        "parent": None,
        "inputs": {
            "NUM": _number_input(num)
        },
        "fields": {},
        "shadow": False,
        "topLevel": False
    })] + num


def _member_proc_call(node: dict, env) -> list:
    def expect_args(expected):
        """Raise an exception if count != provided."""
        if expected != len(node['args']):
            raise TypeError(
                f"{node['caller']}.{node['name']}() expected {expected} \
arguments but {len(node['args'])} were provided")

    caller_type, caller = resolve_ident(node["caller"], env)
    if caller_type == "var":
        raise AttributeError(
            f"Variable '{node['caller']} has no procedure '{node['name']}'")
    if caller_type == "proc":
        raise AttributeError(
            f"Procedure '{node['caller']} has no procedure '{node['name']}'")
    if caller_type == "list":

        def unknown_proc(_, __):
            raise AttributeError(
                f"List '{node['caller']}' has no procedure '{node['name']}'")

        def append(list_id, args):
            expect_args(1)

            value = scratchify(args[0], env)
            _assign_parent(node["id"], value)
            return [(node["id"], {
                "opcode": "data_addtolist",
                "next": None,
                "parent": None,
                "inputs": {
                    "ITEM": _number_input(value)
                },
                "fields": {
                    "LIST": [node["caller"], list_id]
                },
                "shadow": False,
                "topLevel": False
            })] + value

        def clear(list_id, _):
            expect_args(0)

            return [(node["id"], {
                "opcode": "data_deletealloflist",
                "next": None,
                "parent": None,
                "inputs": {},
                "fields": {
                    "LIST": [node["caller"], list_id]
                },
                "shadow": False,
                "topLevel": False
            })]

        def insert(list_id, args):
            expect_args(2)

            index = scratchify(args[0], env)
            value = scratchify(args[1], env)
            _assign_parent(node["id"], value, index)
            return [(node["id"], {
                "opcode": "data_insertatlist",
                "next": None,
                "parent": None,
                "inputs": {
                    "ITEM": _number_input(value),
                    "INDEX": _number_input(index)
                },
                "fields": {
                    "LIST": [node["caller"], list_id]
                },
                "shadow": False,
                "topLevel": False
            })] + value + index

        return {
            "append": append,
            "clear": clear,
            "insert": insert,
        }.get(node["name"], unknown_proc)(caller, node["args"])

    return None


def _program(node: dict, env):
    for var in node["stage"]["variables"]:
        var["id"] = next(id_maker)
    for lst in node["stage"]["lists"]:
        lst["id"] = next(id_maker)
    for spr in node["sprites"]:
        for var in spr["variables"]:
            var["id"] = next(id_maker)
        for lst in spr["lists"]:
            lst["id"] = next(id_maker)

    stage = scratchify(node["stage"], {
        "stage": node["stage"],
        "sprite": node["stage"]
    })

    targets = [
        stage, *(scratchify(spr, {
            "stage": node["stage"],
            "sprite": spr,
            "index": i
        }) for i, spr in enumerate(node["sprites"]))
    ]

    return {
        "targets": targets,
        "monitors": [],
        "meta": {
            "semver": "3.0.0",
            "vm": "0.0.0",
            "agent": ""
        }
    }


SCRATCHIFY_DICT = {
    "operator_add": _bin_numeric_op("operator_add"),
    "operator_subtract": _bin_numeric_op("operator_subtract"),
    "operator_multiply": _bin_numeric_op("operator_multiply"),
    "operator_divide": _bin_numeric_op("operator_divide"),
    "operator_mod": _bin_numeric_op("operator_mod"),
    "operator_equals": _binary_logic_operator("operator_equals"),
    "operator_gt": _binary_logic_operator("operator_gt"),
    "operator_lt": _binary_logic_operator("operator_lt"),
    "operator_and": _binary_logic_operator("operator_and"),
    "operator_or": _binary_logic_operator("operator_or"),
    "operator_not": _operator_not,
    "operator_random": _operator_random,
    "operator_join": _operator_join,
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
    "data_itemoflist": _data_itemoflist,
    "ident": _ident,
    "stage_def": _stage_def,
    "sprite_def": _sprite_def,
    "program": _program,
    "param": _param,
    "motion_movesteps": _motion_movesteps,
    "motion_gotoxy": _motion_gotoxy,
    "motion_turnright": _motion_turnright,
    "motion_turnleft": _motion_turnleft,
    "motion_pointindirection": _motion_pointindirection,
    "motion_glidesecstoxy": _motion_glidesecstoxy,
    "motion_ifonedgebounce": _block_noargs("motion_ifOnEdgeBounce"),
    "looks_say": _looks_say,
    "looks_sayforsecs": _looks_sayforsecs,
    "sensing_askandwait": _sensing_askandwait,
    "sensing_answer": _block_noargs("sensing_answer"),
    "sensing_timer": _block_noargs("sensing_timer"),
    "sensing_username": _block_noargs("sensing_username"),
    "sensing_mousex": _block_noargs("sensing_mousex"),
    "sensing_mousey": _block_noargs("sensing_mousey"),
    "operator_round": _operator_round,
    "member_proc_call": _member_proc_call,
    "pen_pendown": _block_noargs("pen_penDown"),
    "pen_penup": _block_noargs("pen_penUp"),
    "pen_stamp": _block_noargs("pen_stamp"),
    "pen_eraseall": _block_noargs("pen_clear"),
}


def scratchify(tree, env=None) -> list:
    """Converts an AST into a valid object for the project.json file in a
    scratch project."""
    if isinstance(tree, dict):
        if tree["type"] not in ("stage_def", "sprite_def", "ident", "program"):
            tree["id"] = next(id_maker)
        return SCRATCHIFY_DICT[tree["type"]](tree, env)
    if isinstance(tree, (int, float)):
        return [[[4, tree]]]
    if isinstance(tree, str):
        return [[[10, tree]]]
    return tree
