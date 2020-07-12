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


def resolve_list(name: str, env) -> str:
    """Finds the list with specified name in env."""
    for lst in itertools.chain(env["sprite"]["lists"], env["stage"]["lists"]):
        if lst["name"] == name:
            return lst["id"]
    raise NameError(f"List '{name}' does not exist")


def resolve_var_or_list(name: str, env):
    """Finds the variable or list with specified name in env."""
    for owner in env["sprite"], env["stage"]:
        for var in owner["variables"]:
            if var["name"] == name:
                return "var", var["id"]
        for lst in owner["lists"]:
            if lst["name"] == name:
                return "list", lst["id"]
    raise NameError(f"Variable or list '{name}' does not exist")


def resolve_proc(name: str, env) -> str:
    """Finds the procedure with specified name in env."""
    for proc in env["sprite"]["procedures"]:
        if proc["name"] == name:
            return proc
    raise NameError(f"Procedure '{name}' does not exist")


def resolve_ident(name: str, env) -> str:
    """Finds the variable, list, procedure or sprite with specified name in
    env."""
    for var in env["sprite"]["variables"]:
        if var["name"] == name:
            return "var", var["id"]
    for lst in env["sprite"]["lists"]:
        if lst["name"] == name:
            return "list", lst["id"]
    for proc in env["sprite"]["procedures"]:
        if proc["name"] == name:
            return "proc", proc
    for var in env["stage"]["variables"]:
        if var["name"] == name:
            return "var", var["id"]
    for lst in env["stage"]["lists"]:
        if lst["name"] == name:
            return "list", lst["id"]
    if name == "stage":
        return "stage", env["stage"]
    raise NameError(f"Name '{name}' is not defined")
