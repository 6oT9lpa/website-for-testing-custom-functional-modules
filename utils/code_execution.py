import traceback
import json
from flask import current_app as app

def safe_exec(code, globals_dict=None, locals_dict=None):
    """
    Safely execute user-provided code with restricted builtins.
    """
    if globals_dict is None:
        globals_dict = {}
    if locals_dict is None:
        locals_dict = {}

    # Define safe builtins
    safe_builtins = {
        'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool, 'bytearray': bytearray,
        'bytes': bytes, 'chr': chr, 'complex': complex, 'dict': dict, 'divmod': divmod,
        'enumerate': enumerate, 'filter': filter, 'float': float, 'format': format,
        'frozenset': frozenset, 'hash': hash, 'hex': hex, 'id': id, 'int': int,
        'isinstance': isinstance, 'issubclass': issubclass, 'iter': iter, 'len': len,
        'list': list, 'map': map, 'max': max, 'min': min, 'next': next, 'oct': oct,
        'ord': ord, 'pow': pow, 'print': print, 'range': range, 'repr': repr,
        'reversed': reversed, 'round': round, 'set': set, 'slice': slice, 'sorted': sorted,
        'str': str, 'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip,
        'Exception': Exception, 'ValueError': ValueError, 'TypeError': TypeError,
        'KeyError': KeyError, 'IndexError': IndexError, 'AttributeError': AttributeError,
        'ImportError': ImportError, 'NameError': NameError, 'SyntaxError': SyntaxError,
        'RuntimeError': RuntimeError, 'OSError': OSError, 'IOError': IOError,
        'ZeroDivisionError': ZeroDivisionError, 'ArithmeticError': ArithmeticError,
        'LookupError': LookupError, 'SystemError': SystemError, 'NotImplementedError': NotImplementedError,
        'BaseException': BaseException, 'StopIteration': StopIteration, 'GeneratorExit': GeneratorExit,
        'KeyboardInterrupt': KeyboardInterrupt, 'SystemExit': SystemExit, 'Warning': Warning,
        'DeprecationWarning': DeprecationWarning, 'PendingDeprecationWarning': PendingDeprecationWarning,
        'RuntimeWarning': RuntimeWarning, 'FutureWarning': FutureWarning, 'ImportWarning': ImportWarning,
        'UnicodeWarning': UnicodeWarning, 'BytesWarning': BytesWarning, 'ResourceWarning': ResourceWarning,
        'UserWarning': UserWarning, 'SyntaxWarning': SyntaxWarning, 'UnicodeError': UnicodeError,
        'UnicodeDecodeError': UnicodeDecodeError, 'UnicodeEncodeError': UnicodeEncodeError,
        'UnicodeTranslateError': UnicodeTranslateError, 'AssertionError': AssertionError,
        'EOFError': EOFError, 'FileExistsError': FileExistsError, 'FileNotFoundError': FileNotFoundError,
        'InterruptedError': InterruptedError, 'IsADirectoryError': IsADirectoryError,
        'NotADirectoryError': NotADirectoryError, 'PermissionError': PermissionError,
        'ProcessLookupError': ProcessLookupError, 'TimeoutError': TimeoutError,
        'BlockingIOError': BlockingIOError, 'ChildProcessError': ChildProcessError,
        'ConnectionError': ConnectionError, 'BrokenPipeError': BrokenPipeError,
        'ConnectionAbortedError': ConnectionAbortedError, 'ConnectionRefusedError': ConnectionRefusedError,
        'ConnectionResetError': ConnectionResetError, 'FileNotFoundError': FileNotFoundError,
        'ReferenceError': ReferenceError, 'MemoryError': MemoryError, 'BufferError': BufferError,
        'EncodingWarning': EncodingWarning, 'open': open, 'input': input, 'eval': eval,
        'exec': exec, 'compile': compile, 'dir': dir, 'globals': globals, 'locals': locals,
        'vars': vars, 'callable': callable, 'hasattr': hasattr, 'getattr': getattr,
        'setattr': setattr, 'delattr': delattr, 'property': property, 'classmethod': classmethod,
        'staticmethod': staticmethod, 'super': super, 'object': object, 'type': type,
        'None': None, 'True': True, 'False': False, '__import__': __import__,
        '__build_class__': __build_class__, '__name__': '__main__', '__doc__': None,
        '__package__': None, '__spec__': None, '__annotations__': {}, '__file__': None,
        '__cached__': None, '__loader__': None, '__debug__': __debug__,
    }

    globals_dict['__builtins__'] = safe_builtins
    exec(code, globals_dict, locals_dict)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']