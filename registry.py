""" Functions for registering and executing tools to be used by the REPL """

import importlib
import os
import shlex

TOOLS = {}


def register_tool(name, help_text=""):
    """Decorator to register a tool command."""
    def decorator(func):
        TOOLS[name] = {
            "func": func,
            "help": help_text
        }
        return func
    return decorator


def load_tools(tools_dir="tools"):
    """Scans the tools directory and imports all modules."""
    for filename in os.listdir(tools_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            importlib.import_module(f"{tools_dir}.{module_name}")


def execute_command(command_str):
    """Parses input text and routes execution to the registered tool."""
    if not command_str.strip():
        return ""

    parts = shlex.split(command_str)
    cmd, args = parts[0].lower(), parts[1:]

    if cmd in TOOLS:
        try:
            return TOOLS[cmd]["func"](*args)
        except TypeError as e:
            return f"Err: Invalid args"
        except Exception as e:
            return f"Err: {str(e)[:12]}"

    return f"Unknown: {cmd}"
