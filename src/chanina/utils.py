import os
import sys
import random
import datetime
from enum import Enum
from typing import Literal
from types import ModuleType

from colorama import Fore, Back, Style


LEVEL_MAP = {
    0: lambda k: c_ok("Info: ") if not k else c_ok(k),
    1: lambda k: c_warn("Warning: ") if not k else c_warn(k),
    2: lambda k: c_err("Error: ") if not k else c_err(k)
}


class Colors(Enum):
    worker = Back.MAGENTA
    err = Fore.RED
    ok = Fore.GREEN
    warn = Fore.YELLOW
    reset = Style.RESET_ALL


def random_color_picker() -> str:
    colors = list(vars(Back).keys())
    colors.remove("RESET")
    colors.remove("WHITE")
    colors.remove("RED")
    n = random.randint(0, len(colors) - 1)
    choice = colors[n]
    return getattr(Back, choice)


# color utils
def c_err(s: str) -> str: return f"{Colors.err.value}{s}{Colors.reset.value}"
def c_ok(s: str) -> str: return f"{Colors.ok.value}{s}{Colors.reset.value}"
def c_warn(s: str) -> str: return f"{Colors.warn.value}{s}{Colors.reset.value}"
def c_worker(s: str, c: str) -> str: return f"{c}[{s}]{Colors.reset.value}"


# string utils
def s_now() -> str: return datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S")
def s_id(k: str, c: str) -> str: return c_worker(k, c) if k else ""


def log(s: str = "", k: str = "", l: Literal[-1, 0, 1, 2] = 0, c: str = "") -> str:
    """ log prettifier :
    s: str - string to print.
    k: str - key at start of the log
    l: Literal[-1, 0, 1, 2] - color the key according to the LEVEL_MAP.
    """
    msg = f"{s_now()} - {s_id(k, c)} {LEVEL_MAP[l]('')} {s}"
    print(msg)
    return s


class RuntimeLocator:
    """ Handling of the __name__ variable being passed by the current user of
    Chanina instance.
    It's mandatory for the functioning of Chanina that this doesn't fail.
    """
    @staticmethod
    def get_runtime_dir(import_name: str) -> str:
        """ import_name is the module from which the caller is ...
        Well calling.
        """
        module = sys.modules.get(import_name)
        if not isinstance(module, ModuleType) or not hasattr(module, "__file__"):
            raise ValueError(f"Module '{import_name}' has no __file__ attribute")

        assert module.__file__ is not None
        root_path: str = os.path.dirname(os.path.abspath(module.__file__))
        return root_path + "/"
