# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveTrueObject
from tinySelf.vm.primitives import PrimitiveFalseObject


def test_PrimitiveFalseObject():
    assert PrimitiveFalseObject()


def test_PrimitiveFalseObject_is():
    o = PrimitiveFalseObject()

    is_slot = o.slot_lookup("is:")
    result = is_slot.map.primitive_code(None, o, [PrimitiveFalseObject()])
    assert result == PrimitiveTrueObject()

    is_slot = o.slot_lookup("is:")
    result = is_slot.map.primitive_code(None, o, [PrimitiveIntObject(3)])
    assert result == PrimitiveFalseObject()

    is_slot = o.slot_lookup("is:")
    result = is_slot.map.primitive_code(None, o, [PrimitiveTrueObject()])
    assert result == PrimitiveFalseObject()
