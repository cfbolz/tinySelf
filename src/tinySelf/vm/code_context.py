# -*- coding: utf-8 -*-
from rply.token import BaseBox

from tinySelf.vm.bytecodes import *
from tinySelf.vm.object_layout import Object


class LiteralBox(BaseBox):
    def finalize(self):
        pass


class IntBox(LiteralBox):
    def __init__(self, value):
        assert isinstance(value, int)

        self.value = value
        self.literal_type = LITERAL_TYPE_INT

    def __str__(self):
        return str(self.value)


class FloatBox(LiteralBox):
    def __init__(self, value):
        assert isinstance(value, float)

        self.value = value
        self.literal_type = LITERAL_TYPE_FLOAT

    def __str__(self):
        return str(self.value)


class StrBox(LiteralBox):
    def __init__(self, value):
        assert isinstance(value, str)

        self.value = value
        self.literal_type = LITERAL_TYPE_STR

    def __str__(self):
        return self.value


class ObjBox(LiteralBox):
    def __init__(self, obj):
        assert isinstance(obj, Object)

        self.value = obj
        self.literal_type = LITERAL_TYPE_OBJ

    def finalize(self):
        if self.value and self.value.code_context:
            self.value.code_context.finalize()

    def __str__(self):
        if self.value.ast is not None:
            return self.value.ast.__str__()

        return "No obj representation"


class CodeContext(object):
    def __init__(self):
        self._finalized = False

        self.bytecodes = ""
        self._mutable_bytecodes = []
        self._original_bytecodes = ""

        self.str_literal_cache = {}

        self.literals = []
        self._params_cache = None  # used to cache intermediate parameters obj
        self._parent_cache = None

        self.recompile = False
        self.is_recompiled = False

    def add_literal(self, literal):
        assert isinstance(literal, LiteralBox)

        self.literals.append(literal)
        return len(self.literals) - 1

    def add_literal_str(self, literal):
        index = self.str_literal_cache.get(literal, -1)
        if index > -1:
            return index

        index = self.add_literal(StrBox(literal))
        self.str_literal_cache[literal] = index

        return index

    def add_literal_int(self, literal):
        return self.add_literal(IntBox(literal))

    def add_literal_float(self, literal):
        return self.add_literal(FloatBox(literal))

    def add_literal_obj(self, literal):
        return self.add_literal(ObjBox(literal))

    def add_bytecode(self, bytecode):
        self._mutable_bytecodes.append(bytecode)

    def add_literal_str_push_bytecode(self, literal):
        assert isinstance(literal, str)

        index = self.add_literal_str(literal)

        self.add_bytecode(BYTECODE_PUSH_LITERAL)
        self.add_bytecode(LITERAL_TYPE_STR)
        self.add_bytecode(index)

        return index

    def finalize(self):
        if self._finalized:
            return self

        if self._mutable_bytecodes:
            # 4x as 3 is maximum length of multi-bytecode instructions
            self._mutable_bytecodes.append(BYTECODE_RETURN_TOP)
            self._mutable_bytecodes.append(BYTECODE_RETURN_TOP)
            self._mutable_bytecodes.append(BYTECODE_RETURN_TOP)
            self._mutable_bytecodes.append(BYTECODE_RETURN_TOP)

        # I would use bytearray(), but it behaves differently under rpython
        self.bytecodes = str("".join([chr(x) for x in self._mutable_bytecodes]))
        self._mutable_bytecodes = None
        self.str_literal_cache = None

        for item in self.literals:
            item.finalize()

        self._finalized = True

        return self

    def swap_bytecodes(self, bytecodes):
        if not self._original_bytecodes:
            self._original_bytecodes = bytecodes

        self.bytecodes = bytecodes
        self.is_recompiled = True

    def invalidate_bytecodes(self):
        if self._original_bytecodes:
            self.bytecodes = self._original_bytecodes
            self.is_recompiled = False
            self._original_bytecodes = ""

    def debug_repr(self):
        out = '(|\n  literals = (| l <- dict clone. |\n    l\n'
        for cnt, i in enumerate(self.literals):
            out += '      at: %d Put: "%s(%s)";\n' % (cnt, i.__class__.__name__, i.__str__())

        # meh, rpython and his proven non-negative bounds..
        index = len(out) - 2
        assert index >= 0
        out = out[:index] + '.\n  ).\n\n'

        out += '  disassembled = (||\n'
        instructions = []
        for instruction in disassemble(self.bytecodes):
            instruction_as_obj = ", ".join(['"%s"' % str(x) for x in instruction])
            instruction_as_obj = str(instruction_as_obj).replace("'", '"')
            instructions.append('    (%s)' % instruction_as_obj)
        out += ", \n".join(instructions)
        out += '\n  ).\n\n'

        bytecodes_list = ", ".join([str(ord(x)) for x in self.bytecodes])
        out += 'bytecodes = (||\n    %s\n).' % bytecodes_list

        return out
