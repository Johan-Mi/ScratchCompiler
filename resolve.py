"""This module contains functions for finding variables, lists, procedures, etc
by their names."""
import itertools


def resolve_var(name: str, env) -> str:
    """Finds the variable with specified name in env."""
    for var in itertools.chain(env["sprite"]["variables"],
                               env["stage"]["variables"]):
        if var["name"] == name:
            return var["id"]
    raise NameError(f"Variable '{name}' does not exist")


def resolve_arr(name: str, env) -> str:
    """Finds the list with specified name in env."""
    for arr in itertools.chain(env["sprite"]["lists"], env["stage"]["lists"]):
        if arr["name"] == name:
            return arr["id"]
    raise NameError(f"Array '{name}' does not exist")


def resolve_var_or_arr(name: str, env):
    """Finds the variable or list with specified name in env."""
    for owner in env["sprite"], env["stage"]:
        for var in owner["variables"]:
            if var["name"] == name:
                return "var", var["id"]
        for arr in owner["lists"]:
            if arr["name"] == name:
                return "arr", arr["id"]
    raise NameError(f"Variable or array '{name}' does not exist")


def resolve_proc(name: str, env) -> str:
    """Finds the procedure with specified name in env."""
    for proc in env["sprite"]["procedures"]:
        if proc["name"] == name:
            return proc
    raise NameError(f"Procedure '{name}' does not exist")


def resolve_ident(name: str, env) -> str:
    """Finds the variable, array, procedure or sprite with specified name in
    env."""
    for var in env["sprite"]["variables"]:
        if var["name"] == name:
            return "var", var["id"]
    for arr in env["sprite"]["lists"]:
        if arr["name"] == name:
            return "arr", arr["id"]
    for proc in env["sprite"]["procedures"]:
        if proc["name"] == name:
            return "proc", proc
    for var in env["stage"]["variables"]:
        if var["name"] == name:
            return "var", var["id"]
    for arr in env["stage"]["lists"]:
        if arr["name"] == name:
            return "arr", arr["id"]
    if name == "stage":
        return "stage", env["stage"]
    raise NameError(f"Name '{name}' is not defined")
