# Portions Copyright (c) 2005 Nokia Corporation 
import __future__

_features = [getattr(__future__, fname)
             for fname in __future__.all_feature_names]

__all__ = ["compile_command", "Compile", "CommandCompiler"]

def _maybe_compile(compiler, source, filename, symbol):
    # Check for source consisting of only blank lines and comments
    for line in source.split("\n"):
        line = line.strip()
        if line and line[0] != '#':
            break               # Leave it alone
    else:
        source = "pass"         # Replace it with a 'pass' statement

    err = err1 = err2 = None
    code = code1 = code2 = None

    try:
        code = compiler(source, filename, symbol)
    except SyntaxError, err:
        pass

    try:
        code1 = compiler(source + "\n", filename, symbol)
    except SyntaxError, err1:
        pass

    try:
        code2 = compiler(source + "\n\n", filename, symbol)
    except SyntaxError, err2:
        pass

    if code:
        return code
    try:
        e1 = err1.__dict__
    except AttributeError:
        e1 = err1
    try:
        e2 = err2.__dict__
    except AttributeError:
        e2 = err2
    if not code1 and e1 == e2:
        raise SyntaxError, err1

def compile_command(source, filename="<input>", symbol="single"):
    return _maybe_compile(compile, source, filename, symbol)

class Compile:
    def __init__(self):
        self.flags = 0

    def __call__(self, source, filename, symbol):
        codeob = compile(source, filename, symbol, self.flags, 1)
        for feature in _features:
            if codeob.co_flags & feature.compiler_flag:
                self.flags |= feature.compiler_flag
        return codeob

class CommandCompiler:
    def __init__(self,):
        self.compiler = Compile()

    def __call__(self, source, filename="<input>", symbol="single"):
        return _maybe_compile(self.compiler, source, filename, symbol)
