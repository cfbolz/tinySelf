# -*- coding: utf-8 -*-
from bytecodes import *
from primitives import PrimitiveNilObject


class Frame(object):
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def pop_or_nil(self):
        if self.stack:
            return self.pop()

        return PrimitiveNilObject()



class ScopedFrame(Frame):
    def __init__(self, parameters):
        super(ScopedFrame, self).__init__()

        self.variables = {}
        self.parameters = parameters



# class SingleLevelScopedFrame(Frame):
    # def __init__(self, parameters)


class Interpreter(object):
    def __init__(self, universe):
        self.universe = universe

    def interpret(self, code_obj, frame):
        bc_index = 0

        while True:
            bytecode = code_obj.get_bytecode(bc_index)

            if bytecode == BYTECODE_SEND:
                bc_index = self._do_send(bc_index, code_obj, frame)
            # elif bytecode == BYTECODE_SELFSEND:
            #     self._do_selfSend(bc_index, code_obj, frame)
            # elif bytecode == BYTECODE_RESEND:
            #     self._do_resend(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_PUSHSELF:
                bc_index = self._do_pushSelf(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_PUSHLITERAL:
                bc_index = self._do_pushLiteral(bc_index, code_obj, frame)
            # elif bytecode == BYTECODE_POP:
            #     self._do_pop(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_RETURNTOP:
                bc_index = self._do_returnTop(bc_index, code_obj, frame)
            # elif bytecode == BYTECODE_RETURNIMPLICIT:
            #     self._do_returnImplicit(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_ADD_SLOT:
                bc_index = self._do_add_slot(bc_index, code_obj, frame)

            bc_index += 1

    def _put_together_parameters(self, parameter_names, parameters):
        if len(parameter_names) < len(parameters):
            raise ValueError("Too many parameters!")

        return {
            parameter_name: parameters.pop(0)
            for parameter_name in parameter_names
        }

    def _do_send(self, bc_index, code_obj, frame):
        """
        Args:
            bc_index (int): Index of the bytecode in `code_obj` bytecode list.
            code_obj (obj): :class:`CodeContext` instance.
            frame (obj): :class:`Frame` instance.

        Returns:
            int: Index of next bytecode.
        """
        message_type = code_obj.get_bytecode(bc_index + 1)
        number_of_parameters = code_obj.get_bytecode(bc_index + 2)

        message = frame.pop()
        message_name = message.value  # unpack from StrBox

        parameters_values = []
        if message_type == SEND_TYPE_BINARY:
            parameters_values = [frame.pop()]
        elif message_type == SEND_TYPE_KEYWORD:
            for _ in range(number_of_parameters):
                parameters_values.append(frame.pop())

        obj = frame.pop()

        value_of_slot = obj.get_slot(message_name)
        if value_of_slot is None:
            # TODO: parent lookup
            value_of_slot = obj.get_slot_from_parents(message_name)
        else:
            raise ValueError("TODO: not implemented yet (missing slot err)")

        if value_of_slot.has_code:
            parameters_dict = self._put_together_parameters(
                parameter_names=value_of_slot.map.parameters,
                parameters=parameters_values
            )
            sub_frame = ScopedFrame(parameters_dict)
            self.interpret(value_of_slot.map.code, sub_frame)

            return_value = sub_frame.pop_or_nil()

        elif value_of_slot.has_primitive_code:
            return_value = value_of_slot.map.primitive_code(*parameters_values)

        else:
            return_value = value_of_slot

        frame.push(return_value)

        return bc_index + 2

    # def _do_selfSend(self, bc_index, code_obj, frame):
    #     pass

    # def _do_resend(self, bc_index, code_obj, frame):
    #     pass

    def _do_pushSelf(self, bc_index, code_obj, frame):
        pass

    def _do_pushLiteral(self, bc_index, code_obj, frame):
        pass

    # def _do_pop(self, bc_index, code_obj, frame):
    #     pass

    def _do_returnTop(self, bc_index, code_obj, frame):
        pass

    # def _do_returnImplicit(self, bc_index, code_obj, frame):
    #     pass

    def _do_add_slot(self, bc_index, code_obj, frame):
        boxed_value = frame.pop()
        boxed_slot_name = frame.pop()
        boxed_obj = frame.pop()

        slot_type = code_obj.get_bytecode(bc_index + 1)
        if slot_type == SLOT_NORMAL:
            result = boxed_obj.value.meta_add_slot(
                slot_name=boxed_slot_name.value,
                value=boxed_value.value,
            )
        elif slot_type == SLOT_PARENT:
            result = boxed_obj.value.meta_add_parent(
                slot_name=boxed_slot_name.value,
                value=boxed_value.value,
            )
        else:
            raise ValueError("Unknown slot type in ._do_add_slot()!")
        
        if not result:
            raise ValueError("Couldn't add slot!")

        # keep the receiver on the top of the stack
        frame.push(boxed_obj)

        return bc_index + 1