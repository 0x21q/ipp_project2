#!/usr/bin/python3.10
import argparse, re, os.path, sys
import xml.etree.ElementTree as ET
from collections import deque
from enum import Enum

import check_xml

# Stack implementation using deque
class Stack:
    def __init__(self):
        self._stack = deque()
    
    def push(self, data):
        self._stack.append(data)

    def pop(self):
        if len(self._stack) > 0:
            return self._stack.pop()
    
    def top(self):
        if len(self._stack) > 0:
            return self._stack[-1]
    
    def empty(self):
        self._stack.clear()

class Program:
    def  __init__(self):
        self.instructions = []
        self._data_stack = Stack()
        self._frame_stack = Stack()
        self._call_stack = Stack()
        self._global_frame = self.Frame(TypeFrame.GLOBAL) 
        self._label_frame = self.Frame(TypeFrame.LABEL)
        self._temp_frame = None
        self._program_counter = None

    # add instruction to program
    def add_instr(self, instr):
        self.instructions.append(instr)

    # get global frame
    def gf(self):
        return self._global_frame

    # get local frame
    def lf(self):
        return self._frame_stack.top()

    def push_stack(self, data, stack_type):
        match stack_type:
            case TypeStack.DATA:
                self._data_stack.push(data)
            case TypeStack.FRAME:
                self._frame_stack.push(data)
            case TypeStack.CALL:
                self._call_stack.push(data)
            case _:
                print("ERROR: Invalid stack type", file=sys.stderr)

    def pop_stack(self, stack_type):
        match stack_type:
            case TypeStack.DATA:
                return self._data_stack.pop()
            case TypeStack.FRAME:
                return self._frame_stack.pop()
            case TypeStack.CALL:
                return self._call_stack.pop()
            case _:
                print("ERROR: Invalid stack type", file=sys.stderr)

    def top_stack(self, stack_type):
        match stack_type:
            case TypeStack.DATA:
                return self._data_stack.top()
            case TypeStack.FRAME:
                return self._frame_stack.top()
            case TypeStack.CALL:
                return self._call_stack.top()
            case _:
                print("ERROR: Invalid stack type", file=sys.stderr)
    
    # get temp frame
    def tf(self):
        return self._temp_frame

    # set temp frame
    def set_tf(self, frame):
        self._temp_frame = frame

    # get program counter
    def get_pc(self):
        return self._program_counter
    
    # increment program counter
    def set_pc(self, value):
        self._program_counter = value

    # get label frame
    def get_label_frame(self):
        return self._label_frame

    def run(self):
        self.set_pc(0)
        while self.get_pc() < len(self.instructions):
            self.instructions[self.get_pc()].execute(self)

    # for debugging
    def print_frames(self):
        print("\n[GLOBAL FRAME]", file=sys.stderr)
        self.gf().print()
        print("\n[LOCAL FRAME]", file=sys.stderr)
        if self.lf() is not None:
            self.lf().print()
        else:
            print("-> not initialized", file=sys.stderr)
        print("\n[TEMP FRAME]", file=sys.stderr)
        if self.tf() is not None:
            self.tf().print()
        else:
            print("-> not initialized", file=sys.stderr)
        print("\n[LABEL FRAME]", file=sys.stderr)
        self.get_label_frame().print()

    # for debugging
    def __str__(self):
        return f"{self.instructions}"

    class Instruction:
        def __init__(self, address=None, opcode=None, order=None):
            self._address: int = address
            self._opcode: str = opcode
            self._order: int = order
            self.args = []

        def get_address(self):
            return self._address

        def get_opcode(self):
            return self._opcode

        def get_order(self):
            return self._order
        
        def add_arg(self, arg):
            if arg is not None:
                self.args.append(arg)

        def get_arg(self, index):
            if index < len(self.args):
                return self.args[index]
            return None

        def execute(self, program):
            opcode_to_class = {
                "MOVE": program.Move,
                "NOT": program.Not,
                "INT2CHAR": program.Int2char,
                "STRLEN": program.Strlen,
                "TYPE": program.Type,
                "CREATEFRAME": program.Createframe,
                "PUSHFRAME": program.Pushframe,
                "POPFRAME": program.Popframe,
                "RETURN": program.Return,
                "BREAK": program.Break,
                "DEFVAR": program.Defvar,
                "POPS": program.Pops,
                "CALL": program.Call,
                "LABEL": program.Label,
                "JUMP": program.Jump,
                "PUSHS": program.Pushs,
                "WRITE": program.Write,
                "EXIT": program.Exit,
                "DPRINT": program.Dprint,
                "ADD": program.Add,
                "SUB": program.Sub,
                "MUL": program.Mul,
                "IDIV": program.Idiv,
                "LT": program.Lt,
                "GT": program.Gt,
                "EQ": program.Eq,
                "AND": program.And,
                "OR": program.Or,
                "STRI2INT": program.Str2int,
                "CONCAT": program.Concat,
                "GETCHAR": program.Getchar,
                "SETCHAR": program.Setchar,
                "READ": program.Read,
                "JUMPIFEQ": program.Jumpifeq,
                "JUMPIFNEQ": program.Jumpifneq
            }
            return opcode_to_class[self.get_opcode()].execute(self,program)

        class Argument:
            def __init__(self, type=None, value=None):
                self._type: str = type
                if self._type == "int":
                    if re.match(r"^[-+]?[1-9][0-9]*$", value):
                       self._value: int = int(value) 
                    elif re.match(r"^[+-]?(0x|0X)?[0-9]+$", value):
                        self._value: int = int(value, 16)
                    elif re.match(r"^[+-]?0[0-7]+$", value):
                        self._value: int = int(value, 8)
                elif self._type == "bool":
                    if value == "true":
                        self._value: bool = True
                    else:
                        self._value: bool = False
                elif self._type == "nil":
                    self._value: None = None
                else:
                    self._value: str = value

            def get_type(self):
                return self._type

            # only returns something when argument is variable
            def get_frame(self):
                if self._type == "var":
                    return self._value[:2]

            def get_arg_val(self):
                if self._type == "var":
                    return self._value[3:]
                else:
                    return self._value

            # for debugging
            def __str__(self):
                return f"{self._type} {self._value}"

    class Move(Instruction):
        def execute(self, program):
            temp_var = Program.Frame.Var()
            # Checking symbol
            arg = self.get_arg(1)
            match arg.get_type():
                case "var":
                    frame = check_frame_both(self, program, 1)
                    temp_var.set_value(frame.get_var(arg.get_arg_val()))
                case "int":
                    temp_var.set_value(int(arg.get_arg_val()))
                case "bool":
                    temp_var.set_value(bool(arg.get_arg_val()))
                case "string":
                    temp_var.set_value(str(arg.get_arg_val()))
                case "nil":
                    temp_var.set_value(None)
            temp_var.set_type(arg.get_type())
            # Checking variable
            frame = check_frame_declare(self, program, 0)
            frame.set_var(self.get_arg(0).get_arg_val(), temp_var)
            program.set_pc(program.get_pc() + 1)
        
    class Not(Instruction):
        def execute(self, program):
            # Checking symbol
            value = check_selected_type_arg(self, program, 1, "bool")
            # Checking variable and setting value
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_val()).set_type("bool")
            frame.get_var(self.get_arg(0).get_arg_val()).set_value(not value)
            program.set_pc(program.get_pc() + 1)
        
    class Int2char(Instruction):
        def execute(self, program):
            # Checking symbol
            value = check_selected_type_arg(self, program, 1, "int")
            # Checking variable and setting value
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_val()).set_type("string")
            try:
                frame.get_var(self.get_arg(0).get_arg_val()).set_value(chr(value))
            except ValueError:
                print_error(self, "Wrong value of variable", 58)
            program.set_pc(program.get_pc() + 1)
        
    class Strlen(Instruction):
        def execute(self, program):
            # Checking symbol
            value = check_selected_type_arg(self, program, 1, "string")
            # Checking variable and setting value
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_val()).set_type("int")
            frame.get_var(self.get_arg(0).get_arg_val()).set_value(len(value))
            program.set_pc(program.get_pc() + 1)
        
    class Type(Instruction):
        def execute(self, program):
            # Checking symbol
            arg = self.get_arg(1)
            if arg.get_type() == "var":
                frame = check_frame_declare(self, program, 1)
                if frame.vars[arg.get_arg_val()].get_value() is not None:
                    type = frame.get_var(arg.get_arg_val()).get_type()
                else:
                    type = ""
            else:
                type = arg.get_type()
            # Checking variable and setting value
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_val()).set_type("string")
            frame.get_var(self.get_arg(0).get_arg_val()).set_value(str(type))
            program.set_pc(program.get_pc() + 1)

    class Createframe(Instruction):
        def execute(self, program):
            program.set_tf(program.Frame(TypeFrame.TEMP))
    
    class Pushframe(Instruction):
        def execute(self, program):
            if program.tf() is None:
                print_error(self, "Temp frame not initialized", 55)
            program.push_stack(program.tf(), TypeStack.LOCAL)
            program.set_tf(None)
            program.set_pc(program.get_pc() + 1)
        
    class Popframe(Instruction):
        def execute(self, program):
            if program.lf() is None:
                print_error(self, "Local frame not initialized", 55)
            program.set_tf(program.lf())
            program.pop_stack(TypeStack.LOCAL)
            program.set_pc(program.get_pc() + 1)
        
    class Return(Instruction):
        def execute(self, program):
            if program.top_stack(TypeStack.CALL) is None:
                print_error(self, "Call stack is empty", 56)
            program.set_pc(program.top_stack(TypeStack.CALL))
        
    class Break(Instruction):
        def execute(self, program):
            print("Program is on line: ", program.get_pc()+1, file=sys.stderr)
            program.print_frames()
            program.set_pc(program.get_pc() + 1)

    class Defvar(Instruction): 
        def execute(self, program):
            frame_dict = {"GF": program.gf, "LF": program.lf, "TF": program.tf}
            frame_name = self.get_arg(0).get_frame()
            if frame_name not in frame_dict:
                print_error(self, "Invalid frame", 55)
            frame = frame_dict.get(frame_name)()
            if frame is None and frame_name != "GF":
                print_error(self, f"{frame_name} not initialized", 55)
            check_var_exists(self, frame, 0)
            frame.add_var(self.get_arg(0).get_arg_val(), "var")
            program.set_pc(program.get_pc() + 1)

    class Pops(Instruction):
        def execute(self, program):
            frame = check_frame_declare(self, program, 0)
            var = frame.get_var(self.get_arg(0).get_arg_val())
            var.set_type(program.top_stack(TypeStack.DATA).get_type())
            if program.top_stack(TypeStack.DATA).get_type() == "var":
                var.set_value(program.pop_stack(TypeStack.DATA).get_value())
            else:
                var.set_value(program.pop_stack(TypeStack.DATA).get_arg_val())
            program.set_pc(program.get_pc() + 1)
        
    class Call(Instruction):
        def execute(self, program):
            arg = self.get_arg(0)
            # Checking if argument is label and if it exists
            if arg.get_type() != "label" or program.get_label_frame().get_var(arg.get_arg_val()) is None:
                print_error(self, "Invalid label", 52)
            # Saving address of next instruction to call stack and setting pc to label value
            program.push_stack(program.get_pc()+1, TypeStack.CALL)
            program.set_pc(program.get_label_frame().get_var(arg.get_arg_val()).get_value())
    
    class Label(Instruction):
        def execute(self, program):
            #arg = self.get_arg(0)
            #if arg.get_type() != "label" or program.get_label_frame().get_var(arg.get_arg_val()) is not None:
            #    print_error(self, "Invalid label", 52)
            #program.get_label_frame().add_var(arg.get_arg_val(), "label")
            #program.get_label_frame().get_var(arg.get_arg_val()).set_value(self.get_address()+1)
            program.set_pc(program.get_pc() + 1)

    class Jump(Instruction):
        def execute(self, program):
            arg = self.get_arg(0)
            if arg.get_type() != "label" or program.get_label_frame().get_var(arg.get_arg_val()) is None:
                print_error(self, "Invalid label", 52)
            program.set_pc(program.get_label_frame().get_var(arg.get_arg_val()).get_value())
        
    class Pushs(Instruction):
        def execute(self, program):
            arg = self.get_arg(0)
            if arg.get_type() == "var":
                frame = check_frame_both(self, program, 0)
                program.push_stack(frame.get_var(arg.get_arg_val()), TypeStack.DATA)
            else:
                program.push_stack(arg, TypeStack.DATA)
            program.set_pc(program.get_pc() + 1)
        
    class Write(Instruction):
        def execute(self, program):
            arg = self.get_arg(0)
            if arg.get_type() == "var":
                frame = check_frame_both(self, program, 0)
                var = frame.get_var(arg.get_arg_val())
                if var.get_type() == "bool":
                    print("true" if var.get_value() else "false", end='')
                else:
                    print(var.get_value(), end='')
            elif arg.get_type() == "bool":
                print("true" if arg.get_arg_val() else "false", end='')
            elif arg.get_type() == "nil":
                print("", end='')
            else:
                print(arg.get_arg_val(), end='')
            program.set_pc(program.get_pc() + 1)

    class Exit(Instruction):
        def execute(self, program):
            arg = self.get_arg(0)
            if arg.get_type() == "var":
                frame = check_frame_both(self, program, 0)
                value = frame.get_var(arg.get_arg_val()).get_value()
            elif arg.get_type() == "int":
                value = arg.get_arg_val()
            else:
                print_error(self, "Wrong type of argument", 53)

            if not 0 <= int(value) <= 49:
                print_error(self, "Wrong exit code", 57)
            exit(int(value))

    class Dprint(Instruction):
        def execute(self, program):
            arg_type = self.get_arg(0).get_type()
            if arg_type == "var":
                frame = check_frame_both(self, program, 0)
                var = frame.get_var(self.get_arg(0).get_arg_val())
                if var.get_type() == "bool":
                    print("true" if var.get_value() else "false", file=sys.stderr, end='')
                else:
                    print(var.get_value(), file=sys.stderr, end='')
            elif arg_type == "bool":
                print("true" if self.get_arg(0).get_arg_val() else "false", file=sys.stderr, end='')
            elif arg_type == "nil":
                print("", file=sys.stderr, end='')
            else:
                print(self.get_arg(0).get_arg_val(), file=sys.stderr, end='')
            program.set_pc(program.get_pc() + 1)

    class Add(Instruction):
        def execute(self, program):
            value2 = check_selected_type_arg(self, program, 2, "int")
            value1 = check_selected_type_arg(self, program, 1, "int")
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_val()).set_type("int")
            frame.get_var(self.get_arg(0).get_arg_val()).set_value(int(value1 + value2))
            program.set_pc(program.get_pc() + 1)

    class Sub(Instruction):
        def execute(self, program):
            value2 = check_selected_type_arg(self, program, 2, "int")
            value1 = check_selected_type_arg(self, program, 1, "int")
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_val()).set_type("int")
            frame.get_var(self.get_arg(0).get_arg_val()).set_value(int(value1 - value2))
            program.set_pc(program.get_pc() + 1)

    class Mul(Instruction):
        def execute(self, program):
            value2 = check_selected_type_arg(self, program, 2, "int")
            value1 = check_selected_type_arg(self, program, 1, "int")
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_val()).set_type("int")
            frame.get_var(self.get_arg(0).get_arg_val()).set_value(int(value1 * value2))
            program.set_pc(program.get_pc() + 1)

    class Idiv(Instruction):
        def execute(self, program):
            value2 = check_selected_type_arg(self, program, 2, "int")
            if value2 == 0:
                print_error(self, "Division by zero", 57)
            value1 = check_selected_type_arg(self, program, 1, "int")
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_val()).set_type("int")
            frame.get_var(self.get_arg(0).get_arg_val()).set_value(int(value1 / value2))
            program.set_pc(program.get_pc() + 1)

    class Lt(Instruction):
        def execute(self, program):
            if self.get_arg(1).get_type() == "nil" or self.get_arg(2).get_type() == "nil":
                print_error(self, "Wrong type of argument, argument can't be nil", 53)
            arg1_val = get_val(self, program, 1) 
            arg2_val = get_val(self, program, 2)
            if type(arg1_val) != type(arg2_val):
                print_error(self, "Arguments are not the same type", 53)
            frame = check_frame_declare(self, program, 0)
            result_var = frame.get_var(self.get_arg(0).get_arg_val())
            result_var.set_type("bool")
            result_var.set_value(arg1_val < arg2_val)
            program.set_pc(program.get_pc() + 1)

    class Gt(Instruction):
        def execute(self, program):
            if self.get_arg(1).get_type() == "nil" or self.get_arg(2).get_type() == "nil":
                print_error(self, "Wrong type of argument, argument can't be nil", 53)
            arg1_val = get_val(self, program, 1) 
            arg2_val = get_val(self, program, 2)
            if type(arg1_val) != type(arg2_val):
                print_error(self, "Arguments are not the same type", 53)
            frame = check_frame_declare(self, program, 0)
            result_var = frame.get_var(self.get_arg(0).get_arg_val())
            result_var.set_type("bool")
            result_var.set_value(arg1_val > arg2_val)
            program.set_pc(program.get_pc() + 1)

    class Eq(Instruction):
        def execute(self, program):
            arg1_val = get_val(self, program, 1) 
            arg2_val = get_val(self, program, 2)
            if self.get_arg(1).get_type() == "nil" or self.get_arg(2).get_type() == "nil":
                pass
            elif type(arg1_val) != type(arg2_val):
                print_error(self, "Arguements are not the same type and neither is nil", 53)
            frame = check_frame_declare(self, program, 0)
            result_var = frame.get_var(self.get_arg(0).get_arg_val())
            result_var.set_type("bool")
            result_var.set_value(arg1_val == arg2_val)
            program.set_pc(program.get_pc() + 1)

    class And(Instruction):
        def execute(self, program):
            value2 = check_selected_type_arg(self, program, 2, "bool")
            value1 = check_selected_type_arg(self, program, 1, "bool")
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_val()).set_type("bool")
            frame.get_var(self.get_arg(0).get_arg_val()).set_value(value1 and value2)
            program.set_pc(program.get_pc() + 1)

    class Or(Instruction):
        def execute(self, program):
            value2 = check_selected_type_arg(self, program, 2, "bool")
            value1 = check_selected_type_arg(self, program, 1, "bool")
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_val()).set_type("bool")
            frame.get_var(self.get_arg(0).get_arg_val()).set_value(value1 or value2)
            program.set_pc(program.get_pc() + 1)

    class Str2int(Instruction):
        def execute(self, program):
            index = check_selected_type_arg(self, program, 2, "int")
            value = check_selected_type_arg(self, program, 1, "string")
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_val()).set_type("int")
            try:
                frame.get_var(self.get_arg(0).get_arg_val()).set_value(ord(value[index]))
            except IndexError:
                print_error(self, "Index out of range", 58)
            except ValueError:
                print_error(self, "Invalid value of argument", 58)
            program.set_pc(program.get_pc() + 1)
            
    class Concat(Instruction):
        def execute(self, program):
            value2 = check_selected_type_arg(self, program, 2, "string")
            value1 = check_selected_type_arg(self, program, 1, "string")
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_val()).set_type("string")
            frame.get_var(self.get_arg(0).get_arg_val()).set_value(value1 + value2)
            program.set_pc(program.get_pc() + 1)

    class Getchar(Instruction):
        def execute(self, program):
            index = check_selected_type_arg(self, program, 2, "int")
            value = check_selected_type_arg(self, program, 1, "string")
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_val()).set_type("string")
            try:
                frame.get_var(self.get_arg(0).get_arg_val()).set_value(value[index])
            except IndexError:
                print_error(self, "Index out of range", 58)
            program.set_pc(program.get_pc() + 1)

    class Setchar(Instruction):
        def execute(self, program):
            char = check_selected_type_arg(self, program, 2, "string")
            index = check_selected_type_arg(self, program, 1, "int")
            frame = check_frame_both(self, program, 0)
            if frame.get_var(self.get_arg(0).get_arg_val()).get_type() != "string":
                print_error(self, "Wrong type of argument, argument is not a string", 53)
            try:
                frame.get_var(self.get_arg(0).get_arg_val()).set_char(char, index)
            except IndexError:
                print_error(self, "Index out of range", 58)
            program.set_pc(program.get_pc() + 1)

    class Read(Instruction):
        def execute(self, program):
            value = check_selected_type_arg(self, program, 1, "type")
            frame = check_frame_declare(self, program, 0)
            var = frame.get_var(self.get_arg(0).get_arg_val())
            try:
                if value == "int":
                    var.set_type("int")
                    var.set_value(int(input))
                elif value == "bool":
                    var.set_type("bool")
                    var.set_value(True) if input == "true" else var.set_value(False)
                elif value == "string":
                    var.set_type("string")
                    var.set_value(input)
            except ValueError:
                print_error(self, "Invalid type of input value", 58)
            program.set_pc(program.get_pc() + 1)

    class Jumpifeq(Instruction):
        def execute(self, program):
            value2 = get_val(self, program, 2)
            value1 = get_val(self, program, 1) 
            if self.get_arg(1).get_type() == "nil" or self.get_arg(2).get_type() == "nil":
                pass
            elif type(value1) != type(value2):
                print_error(self, "Arguments are not the same type", 53)

            arg = self.get_arg(0)
            if arg.get_type() != "label" or program.get_label_frame().get_var(arg.get_arg_val()) is None:
                print_error(self, "Invalid label", 52)
            if value1 == value2:
                program.set_pc(program.get_label_frame().get_var(arg.get_arg_val()).get_value())
            else:
                program.set_pc(program.get_pc() + 1)

    class Jumpifneq(Instruction):
        def execute(self, program):
            value2 = get_val(self, program, 2)
            value1 = get_val(self, program, 1)
            if self.get_arg(1).get_type() == "nil" or self.get_arg(2).get_type() == "nil":
                pass
            elif type(value1) != type(value2):
                print_error(self, "Arguemnts are not the same type and neither is nil", 53)

            arg = self.get_arg(0)
            if arg.get_type() != "label" or program.get_label_frame().get_var(arg.get_arg_val()) is None:
                print_error(self, "Invalid label", 52)
            if value1 != value2:
                program.set_pc(program.get_label_frame().get_var(arg.get_arg_val()).get_value())
            else:
                program.set_pc(program.get_pc() + 1)

    class Frame:
        def __init__(self,type):
            self.vars = {}
            self._type: TypeFrame = type

        def add_var(self, var_name, type=None):
            self.vars[var_name] = self.Var(type)

        def get_var(self, var_name):
            if var_name in self.vars:
                return self.vars[var_name]
            return None

        def set_var(self, var_name, var):
            self.vars[var_name] = var
        
        def print(self):
            for var in self.vars:
                print("-> type: " + self.vars[var].get_type() + ", [\"" + var + "\" : " + str(self.vars[var].get_value()) + "]")

        # for debugging
        def __str__(self):
            return f"{self.vars}"

        class Var:
            def __init__(self, type=None, value=None):
                self._type: str = type
                self._value = value

            def get_type(self):
                return self._type

            def set_type(self, type):
                self._type = type

            def get_frame(self):
                return super()._type

            def get_value(self):
                return self._value

            def set_value(self, value):
                self._value = value

            def set_char(self, char, index):
                char = char[0] if len(char) > 0 else ""
                self._value = self._value[:index] + char + self._value[index+1:]

            def __str__(self):
                return f"{self._value}"

# Types of frames
class TypeFrame(Enum):
    GLOBAL = 0
    LOCAL = 1
    TEMP = 2
    LABEL = 3

class TypeStack(Enum):
    DATA = 0
    CALL = 1
    FRAME = 2

# Parsing script arguments
def parse_sc_args():
    sc_args = argparse.ArgumentParser(description="Interprets code in XML format")
    sc_args.add_argument("-s","--source", type=str)
    sc_args.add_argument("-i","--input", type=str)
    sc_args_parsed = sc_args.parse_args()
    source = None; input = None
    if sc_args_parsed.source is None and sc_args_parsed.input is None:
        print("ERROR: No source file or input file specified", file=sys.stderr)
        exit(10)
    elif sc_args_parsed.source is None:
        # load source from stdin
        source = sys.stdin.read()
    elif sc_args_parsed.input is None:
        # load input from stdin
        input = sys.stdin.read()

    if source is None:
        if os.path.isfile(sc_args_parsed.source):
            source_file = open(sc_args_parsed.source, "r")
            try:    
                xml = ET.parse(source_file)
            except ET.ParseError:
                print("ERROR: Invalid XML format", file=sys.stderr)
                exit(31)
            xml_root = xml.getroot()
        else:
            print("ERROR: Source file doesn't exists", file=sys.stderr)
            exit(11)
    else:
        try:
            xml_root = ET.fromstring(source)
        except ET.ParseError:
            print("ERROR: Invalid XML format", file=sys.stderr)
            exit(31)

    if input is None:
        if os.path.isfile(sc_args_parsed.input):
            input_file = open(sc_args_parsed.input, "r")
            input = input_file.read()
        else:
            print("ERROR: Input file doesn't exists", file=sys.stderr)
            exit(11)
    return (xml_root, input)

# Checks if given variable already exists
def check_var_exists(instruction, frame, arg_index):
    if instruction.get_arg(arg_index).get_arg_val() in frame.vars:
        print_error(instruction, "Variable already declared", 52)

# Checks if variable is declared
def check_var_declaration(instruction, frame, arg_index):
    if instruction.get_arg(arg_index).get_arg_val() not in frame.vars:
        print_error(instruction, "Variable not declared", 54)

# Checks if variable is defined
def check_var_definition(instruction, frame, arg_index):
    if frame.vars[instruction.get_arg(arg_index).get_arg_val()].get_value() is None:
        print_error(instruction, "Variable not defined", 56)

# Function looks for variable in given frame, checks if it is declared and returns given frame
def check_frame_declare(instruction, program, arg_index):
    if instruction.get_arg(arg_index).get_frame() == "GF":
        check_var_declaration(instruction, program.gf(), arg_index)
        return program.gf()
    elif instruction.get_arg(arg_index).get_frame() == "LF":
        if program.lf() is None:
            print_error(instruction, "Local frame not initialized", 55)
        check_var_declaration(instruction, program.lf(), arg_index)
        return program.lf()
    if instruction.get_arg(arg_index).get_frame() == "TF":
        if program.tf() is None:
            print_error(instruction, "Temp frame not initialized", 55)
        check_var_declaration(instruction, program.tf(), arg_index)
        return program.tf()

# Function looks for variable in given frame, checks if it is declared and defined and returns given frame
def check_frame_both(instruction, program, arg_index):
    if instruction.get_arg(arg_index).get_frame() == "GF":
        check_var_declaration(instruction, program.gf(), arg_index)
        check_var_definition(instruction, program.gf(), arg_index)
        return program.gf()
    elif instruction.get_arg(arg_index).get_frame() == "LF":
        if program.lf() is None:
            print_error(instruction, "Local frame not initialized", 55)
        check_var_declaration(instruction, program.lf(), arg_index)
        check_var_definition(instruction, program.lf(), arg_index)
        return program.lf()
    if instruction.get_arg(arg_index).get_frame() == "TF":
        if program.tf() is None:
            print_error(instruction, "Temp frame not initialized", 55)
        check_var_declaration(instruction, program.tf(), arg_index)
        check_var_definition(instruction, program.tf(), arg_index)
        return program.tf()

# Prints error message
def print_error(instruction, error_msg, error_code):
    print("ERROR on line: " + str(instruction.get_address()+1), file=sys.stderr)
    print("ERROR: " + error_msg, file=sys.stderr)
    exit(error_code)

# Function checks if argument for selected type is correct and return its value
def check_selected_type_arg(self, program, arg_index, type):
    if self.get_arg(arg_index).get_type() == "var":
        frame = check_frame_both(self, program, arg_index)
        if frame.get_var(self.get_arg(arg_index).get_arg_val()).get_type() != type:
            print_error(self, "Wrong type of argument", 53)
        return frame.get_var(self.get_arg(arg_index).get_arg_val()).get_value()
    elif self.get_arg(arg_index).get_type() != type:
        print_error(self, "Wrong type of argument", 53)
    return self.get_arg(arg_index).get_arg_val()

# Function checks if argument is variable or symbol and returns its value
def get_val(instr, program, arg_index):
    arg = instr.get_arg(arg_index)
    if arg.get_type() == "var":
        frame = check_frame_both(instr, program, arg_index)
        return frame.get_var(arg.get_arg_val()).get_value()
    return arg.get_arg_val()

# Generates program structure from XML to objects (classes)
def gen_program(xml_root):
    program = Program()
    address = 0
    for instr in xml_root:
        instr_obj = Program.Instruction(address, instr.attrib["opcode"].upper(), instr.attrib["order"])
        for arg in instr:
            if arg.text is None: 
                arg.text = ""
            arg_obj = Program.Instruction.Argument(arg.attrib["type"], arg.text)
            instr_obj.add_arg(arg_obj)
        program.add_instr(instr_obj)
        # Generates labels
        if instr_obj.get_opcode() == "LABEL":
            gen_label(instr_obj, program)
        address += 1
    return program

def gen_label(instr, program):
    arg = instr.get_arg(0)
    if arg.get_type() != "label" or program.get_label_frame().get_var(arg.get_arg_val()) is not None:
        print_error(instr, "Invalid label", 52)
    program.get_label_frame().add_var(arg.get_arg_val(), "label")
    program.get_label_frame().get_var(arg.get_arg_val()).set_value(instr.get_address()+1)

# Checks if order attributes are without duplicates
def check_order_attribute(program):
    dup_list = []
    for instr in program.instructions:
        if instr.get_order() in dup_list:
            print("ERROR on line: " + str(instr.get_address()+1), file=sys.stderr)
            print("ERROR: Duplicate order attribute", file=sys.stderr)
            exit(32)
        dup_list.append(instr.get_order())

# Sorts instructions by order attribute
def sort_by_order(program):
    program.instructions.sort(key=lambda instr: int(instr.get_order()))
    return program

# Prints program
#def print_program():
    #for instr in prg.instructions:
        #print(str(instr.get_address()) +": ",instr.get_opcode())
        #for arg in instr.args:
            #print(arg.get_type(), arg.get_arg_val())

if __name__ == "__main__":
    xml_root, input = parse_sc_args()
    check_xml.check_xml(xml_root)
    gen_program(xml_root)
    prg = gen_program(xml_root)
    check_order_attribute(prg)
    prg = sort_by_order(prg)
    prg.run()
    exit(0)