"""This module contains the scratchify function, which converts an AST into a
valid object for the project.json file in a scratch project."""


class IdCounter:
    """Generates IDs for blocks, variables, etc."""
    curr_id = 0

    def __call__(self):
        """Returns the next ID."""
        self.curr_id += 1
        return f"_{self.curr_id}"


next_id = IdCounter()


def resolve_var(name: str, env) -> str:
    """Finds the variable with specified name in env."""
    for i in env["sprite"]["variables"]:
        if i["name"] == name:
            return i["id"]
    for i in env["stage"]["variables"]:
        if i["name"] == name:
            return i["id"]
    raise NameError(f"Identifier '{name}' is not defined")


def resolve_var_or_arr(name: str, env) -> str:
    """Finds the variable or list with specified name in env."""
    for i in env["sprite"]["variables"]:
        if i["name"] == name:
            return "var", i["id"]
    for i in env["sprite"]["lists"]:
        if i["name"] == name:
            return "arr", i["id"]
    for i in env["stage"]["variables"]:
        if i["name"] == name:
            return "var", i["id"]
    for i in env["stage"]["lists"]:
        if i["name"] == name:
            return "arr", i["id"]
    raise NameError(f"Identifier '{name}' is not defined")


def resolve_proc(name: str, env) -> str:
    """Finds the procedure with specified name in env."""
    for i in env["sprite"]["procedures"]:
        if i["name"] == name:
            return i
    raise NameError(f"Identifier '{name}' is not defined")


def scratchify(tree, env=None) -> list:
    if isinstance(tree, dict):

        def assign_parent(parent_id: str, *args):
            for i in args:
                if isinstance(i[0], tuple):
                    i[0][1]["parent"] = parent_id

        def doubly_link_stms(first: tuple, rest: list):
            if len(rest) > 0:
                rest[0][0][1]["parent"] = first[0]
                for i in range(len(rest) - 1):
                    rest[i][0][1]["next"] = rest[i + 1][0][0]
                    rest[i + 1][0][1]["parent"] = rest[i][0][0]

        def stage_def(node: dict) -> list:
            return sum((scratchify(i, env) for i in node["procedures"]), [])

        def sprite_def(node: dict) -> list:
            return sum((scratchify(i, env) for i in node["procedures"]), [])

        def procedures_definition(node: dict) -> list:
            node["id"] = next_id()

            params = [scratchify(i, env)[0] for i in node["params"]]

            definition = (node["id"], {
                "opcode": "procedures_definition",
                "next": None,
                "parent": None,
                "inputs": {
                    "custom_block": [1, next_id()]
                },
                "fields": {},
                "shadow": False,
                "topLevel": True,
                "x": 0,
                "y": 0
            })

            prototype = (definition[1]["inputs"]["custom_block"][1], {
                "opcode": "procedures_prototype",
                "next": None,
                "parent": definition[0],
                "inputs": {next_id(): [1, i[0]]
                           for i in params},
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
                    None,
                    "argumentnames":
                    str([i["name"]
                         for i in node["params"]]).replace("'", "\""),
                    "argumentdefaults":
                    str([""] * len(params)).replace("'", "\""),
                    "warp":
                    node["warp"]
                }
            })

            body = [scratchify(i, env) for i in node["body"]]
            if len(body) > 0:
                definition[1]["next"] = body[0][0][0]

            prototype[1]["mutation"]["argumentids"] = str(
                list(prototype[1]["inputs"])).replace("'", "\"")

            for i in params:
                i[1]["parent"] = prototype[0]

            doubly_link_stms(definition, body)

            node["prototype"] = prototype

            params.append(definition)
            params.append(prototype)
            return sum(body, params)

        def param(node: dict) -> list:
            node["id"] = next_id()
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

        def motion_movesteps(node: dict) -> list:
            node["id"] = next_id()
            steps = scratchify(node["STEPS"], env)
            assign_parent(node["id"], steps)
            return [(node["id"], {
                "opcode": "motion_movesteps",
                "next": None,
                "parent": None,
                "inputs": {
                    "STEPS": [1, steps[0][0]]
                },
                "fields": {},
                "shadow": False,
                "topLevel": False
            })] + steps

        def motion_gotoxy(node: dict) -> list:
            node["id"] = next_id()
            x_coord = scratchify(node["X"], env)
            y_coord = scratchify(node["Y"], env)
            assign_parent(node["id"], x_coord, y_coord)
            return [(node["id"], {
                "opcode": "motion_gotoxy",
                "next": None,
                "parent": None,
                "inputs": {
                    "X": [1, x_coord[0][0]],
                    "Y": [1, y_coord[0][0]]
                },
                "fields": {},
                "shadow": False,
                "topLevel": False
            })] + x_coord + y_coord

        def motion_turnright(node: dict) -> dict:
            node["id"] = next_id()
            degrees = scratchify(node["DEGREES"], env)
            assign_parent(node["id"], degrees)
            return [(node["id"], {
                "opcode": "motion_turnright",
                "next": None,
                "parent": None,
                "inputs": {
                    "DEGREES": [1, degrees[0][0]]
                },
                "fields": {},
                "shadow": False,
                "topLevel": False
            })] + degrees

        def motion_turnleft(node: dict) -> dict:
            node["id"] = next_id()
            degrees = scratchify(node["DEGREES"], env)
            assign_parent(node["id"], degrees)
            return [(node["id"], {
                "opcode": "motion_turnleft",
                "next": None,
                "parent": None,
                "inputs": {
                    "DEGREES": [1, degrees[0][0]]
                },
                "fields": {},
                "shadow": False,
                "topLevel": False
            })] + degrees

        def motion_ifonedgebounce(node: dict) -> list:
            node["id"] = next_id()
            return [(node["id"], {
                "opcode": "motion_ifonedgebounce",
                "next": None,
                "parent": None,
                "inputs": {},
                "fields": {},
                "shadow": False,
                "topLevel": False
            })]

        def motion_pointindirection(node: dict) -> list:
            node["id"] = next_id()
            direction = scratchify(node["DIRECTION"], env)
            assign_parent(node["id"], direction)
            return [(node["id"], {
                "opcode": "motion_pointindirection",
                "next": None,
                "parent": None,
                "inputs": {
                    "DIRECTION": [1, direction[0][0]]
                },
                "fields": {},
                "shadow": False,
                "topLevel": False
            })] + direction

        def motion_glidesecstoxy(node: dict) -> list:
            node["id"] = next_id()
            x_coord = scratchify(node["X"], env)
            y_coord = scratchify(node["Y"], env)
            secs = scratchify(node["SECS"], env)
            assign_parent(node["id"], x_coord, y_coord, secs)
            return [(node["id"], {
                "opcode": "motion_glidesecstoxy",
                "next": None,
                "parent": None,
                "inputs": {
                    "X": [1, x_coord[0][0]],
                    "Y": [1, y_coord[0][0]],
                    "SECS": [1, secs[0][0]]
                },
                "fields": {},
                "shadow": False,
                "topLevel": False
            })] + x_coord + y_coord + secs

        def control_if(node: dict) -> list:
            node["id"] = next_id()

            condition = scratchify(node["CONDITION"], env)
            assign_parent(node["id"], condition)

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

            doubly_link_stms(if_stmt, substack)

            return sum(substack, [if_stmt] + condition)

        def control_if_else(node: dict) -> list:
            node["id"] = next_id()

            condition = scratchify(node["CONDITION"], env)
            assign_parent(node["id"], condition)

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

            doubly_link_stms(if_stmt, substack)
            doubly_link_stms(if_stmt, substack2)

            return sum(substack + substack2, [if_stmt] + condition)

        def control_repeat(node: dict) -> list:
            node["id"] = next_id()

            times = scratchify(node["TIMES"], env)
            assign_parent(node["id"], times)

            substack = [scratchify(i, env) for i in node["body"]]

            loop = (node["id"], {
                "opcode": "control_repeat",
                "next": None,
                "parent": None,
                "inputs": {
                    "TIMES": [1, times[0][0]],
                    "SUBSTACK": [2, substack[0][0][0]]
                },
                "fields": {},
                "shadow": False,
                "topLevel": False
            })

            doubly_link_stms(loop, substack)

            return sum(substack, [loop] + times)

        def control_forever(node: dict) -> list:
            node["id"] = next_id()

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

            doubly_link_stms(loop, substack)

            return sum(substack, [loop])

        def control_while(node: dict) -> list:
            node["id"] = next_id()

            condition = scratchify(node["CONDITION"], env)
            assign_parent(node["id"], condition)

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

            doubly_link_stms(loop, substack)

            return sum(substack, [loop] + condition)

        def control_repeat_until(node: dict) -> list:
            node["id"] = next_id()

            condition = scratchify(node["CONDITION"], env)
            assign_parent(node["id"], condition)

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

            doubly_link_stms(loop, substack)

            return sum(substack, [loop] + condition)

        def bin_numeric_op(opcode: str):
            def generated_func(node):
                node["id"] = next_id()
                num1 = scratchify(node["NUM1"], env)
                num2 = scratchify(node["NUM2"], env)
                assign_parent(node["id"], num1, num2)
                return [(node["id"], {
                    "opcode": opcode,
                    "next": None,
                    "parent": None,
                    "inputs": {
                        "NUM1": [1, num1[0][0]],
                        "NUM2": [1, num2[0][0]]
                    },
                    "fields": {},
                    "shadow": False,
                    "topLevel": False
                })] + num1 + num2

            return generated_func

        def binary_logic_operator(opcode: str):
            def generated_func(node):
                node["id"] = next_id()
                operand1 = scratchify(node["OPERAND1"], env)
                operand2 = scratchify(node["OPERAND2"], env)
                assign_parent(node["id"], operand1, operand2)
                return [(node["id"], {
                    "opcode": opcode,
                    "next": None,
                    "parent": None,
                    "inputs": {
                        "OPERAND1": [1, operand1[0][0]],
                        "OPERAND2": [1, operand2[0][0]]
                    },
                    "fields": {},
                    "shadow": False,
                    "topLevel": False
                })] + operand1 + operand2

            return generated_func

        def operator_not(node: dict) -> list:
            node["id"] = next_id()
            operand = scratchify(node["OPERAND"], env)
            assign_parent(node["id"], operand)
            return [(node["id"], {
                "opcode": "operator_not",
                "next": None,
                "parent": None,
                "inputs": {
                    "OPERAND": [1, operand[0][0]]
                },
                "fields": {},
                "shadow": False,
                "topLevel": False
            })] + operand

        def operator_random(node: dict) -> list:
            node["id"] = next_id()
            low = scratchify(node["FROM"], env)
            high = scratchify(node["TO"], env)
            assign_parent(node["id"], low, high)
            return [(node["id"], {
                "opcode": "operator_random",
                "next": None,
                "parent": None,
                "inputs": {
                    "FROM": [1, low[0][0]],
                    "TO": [1, high[0][0]]
                },
                "fields": {},
                "shadow": False,
                "topLevel": False
            })] + low + high

        def data_setvariableto(node: dict) -> list:
            node["id"] = next_id()
            var_id = resolve_var(node["name"], env)
            value = scratchify(node["value"], env)
            return [(node["id"], {
                "opcode": "data_setvariableto",
                "next": None,
                "parent": None,
                "inputs": {
                    "VALUE": [1, value[0][0]]
                },
                "fields": {
                    "VARIABLE": [node["name"], var_id]
                },
                "shadow": False,
                "topLevel": False
            })] + value

        def data_changevariableby(node: dict) -> list:
            node["id"] = next_id()
            var_or_arr, var_id = resolve_var_or_arr(node["name"], env)
            value = scratchify(node["value"], env)
            if var_or_arr == "var":
                return [(node["id"], {
                    "opcode": "data_changevariableby",
                    "next": None,
                    "parent": None,
                    "inputs": {
                        "VALUE": [1, value[0][0]]
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
                    "ITEM": [1, value[0][0]]
                },
                "fields": {
                    "LIST": [node["name"], var_id]
                },
                "shadow": False,
                "topLevel": False
            })] + value

        def procedures_call(node: dict) -> list:
            node["id"] = next_id()

            proc = resolve_proc(node["name"], env)
            args = [scratchify(i, env) for i in node["args"]]
            call = [(node["id"], {
                "opcode": "procedures_call",
                "next": None,
                "parent": None,
                "inputs": {
                    i: [1, j[0][0]]
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

        def ident(node: dict) -> list:
            var_or_arr, var_id = resolve_var_or_arr(node["name"], env)
            return [[[12 if var_or_arr == "var" else 13, node["name"],
                      var_id]]]

        def program(node: dict) -> list:
            for i in node["stage"]["variables"]:
                i["id"] = next_id()
            for i in node["stage"]["lists"]:
                i["id"] = next_id()

            stage = {
                "isStage":
                True,
                "name":
                "Stage",
                "variables":
                {i["id"]: [i["name"], 0]
                 for i in node["stage"]["variables"]},
                "lists":
                {i["id"]: [i["name"], []]
                 for i in node["stage"]["lists"]},
                "broadcasts": {},
                "blocks":
                dict(i for i in scratchify(
                    node["stage"], env or {
                        "stage": node["stage"],
                        "sprite": node["stage"]
                    }) if isinstance(i, tuple)),
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

            targets = [stage]
            for i, spr in enumerate(node["sprites"]):
                for j in spr["variables"]:
                    j["id"] = next_id()
                for j in spr["lists"]:
                    j["id"] = next_id()

                targets.append({
                    "isStage":
                    False,
                    "name":
                    spr["name"],
                    "variables":
                    {j["id"]: [j["name"], 0]
                     for j in spr["variables"]},
                    "lists": {j["id"]: [j["name"], []]
                              for j in spr["lists"]},
                    "broadcasts": {},
                    "blocks":
                    dict(j for j in scratchify(
                        spr, env or {
                            "stage": node["stage"],
                            "sprite": spr
                        }) if isinstance(j, tuple)),
                    "comments": {},
                    "currentCostume":
                    0,
                    "costumes": [],
                    "sounds": [],
                    "volume":
                    0,
                    "layerOrder":
                    i + 1,
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
                })

            return {
                "targets": targets,
                "monitors": [],
                "meta": {
                    "semver": "3.0.0",
                    "vm": "0.0.0",
                    "agent": ""
                }
            }

        return {
            "operator_add": bin_numeric_op("operator_add"),
            "operator_subtract": bin_numeric_op("operator_subtract"),
            "operator_multiply": bin_numeric_op("operator_multiply"),
            "operator_divide": bin_numeric_op("operator_divide"),
            "operator_mod": bin_numeric_op("operator_mod"),
            "operator_equals": binary_logic_operator("operator_equals"),
            "operator_gt": binary_logic_operator("operator_gt"),
            "operator_lt": binary_logic_operator("operator_lt"),
            "operator_and": binary_logic_operator("operator_and"),
            "operator_or": binary_logic_operator("operator_or"),
            "operator_not": operator_not,
            "operator_random": operator_random,
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
            "ident": ident,
            "stage_def": stage_def,
            "sprite_def": sprite_def,
            "program": program,
            "param": param,
            "motion_movesteps": motion_movesteps,
            "motion_gotoxy": motion_gotoxy,
            "motion_turnright": motion_turnright,
            "motion_turnleft": motion_turnleft,
            "motion_pointindirection": motion_pointindirection,
            "motion_glidesecstoxy": motion_glidesecstoxy,
            "motion_ifonedgebounce": motion_ifonedgebounce,
        }.get(tree["type"], lambda x: [])(tree)
    if isinstance(tree, (int, float)):
        return [[[4, tree]]]
    if isinstance(tree, str):
        return [[[10, tree]]]
    return tree
