#
import pathlib

_install_path = pathlib.Path(__file__).resolve().parent
_config_file = f'{_install_path}/PyLex_configs.xlsx'

from .pylex import PyLex
from .tokenizer import Tokenizer
from .lexer import Lexer

