# IPP project 2
# Interpreter for IPPcode23 pseudo-assembly language
# @brief Main project file
# @author Jakub Kratochvil (xkrato67)
# @file interpret.py

import argparse, re, os.path, sys
import xml.etree.ElementTree as ET
from collections import deque
from enum import Enum

import check_xml

# Stack implementation using deque
class Stack:
    # Stack constructor
    def __init__(self):
        self._stack = deque()

    # Push data to stack
    # @param data Data to push
    def push(self, data):
        self._stack.append(data)

    # Pop data from stack
    # @return Popped data
    def pop(self):
        if len(self._stack) > 0:
            return self._stack.pop()
    
    # Get top data from stack
    # @return Top data from stack
    def top(self):
        if len(self._stack) > 0:
            return self._stack[-1]
    
    # Clear stack
    def empty(self):
        self._stack.clear()

class Program:
    # Program constructor
    def  __init__(self):
        self.instructions       : list          = []
        self._data_stack        : Stack         = Stack()
        self._frame_stack       : Stack         = Stack()
        self._call_stack        : Stack         = Stack()
        self._global_frame      : self.Frame    = self.Frame(TypeFrame.GLOBAL) 
        self._label_frame       : self.Frame    = self.Frame(TypeFrame.LABEL)
        self._temp_frame        : self.Frame    = None
        self._program_counter   : int           = None

    # Add instruction to program
    # @param instr instruction to add
    def add_instr(self, instr):
        self.instructions.append(instr)

    # Get global frame
    # @return global frame
    def gf(self):
        return self._global_frame

    # Get local frame
    # @return local frame
    def lf(self):
        return self._frame_stack.top()

    # Get temp frame
    # @return temp frame
    def tf(self):
        return self._temp_frame

    #  Set temp frame
    #  @param frame Frame to set as temp frame
    def set_tf(self, frame):
        self._temp_frame = frame

    # Push data to selected stack
    # @param data Data to push
    # @param stack_type Type of stack
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
                exit(99)

    # Pop data from selected stack
    # @param stack_type Type of stack
    # @return Popped data
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
                exit(99)

    # Get top data from selected stack
    # @param stack_type Type of stack
    # @return Top data from stack
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
                exit(99)

    # Get program counter
    # @return Program counter
    def get_pc(self):
        return self._program_counter
    
    # Increment program counter
    # @param value Value to set program counter to
    def set_pc(self, value):
        self._program_counter = value

    # Get label frame
    # @return Label frame
    def get_label_frame(self):
        return self._label_frame

    # Run all instructions
    def run(self):
        self.set_pc(0)
        while self.get_pc() < len(self.instructions):
            self.instructions[self.get_pc()].execute(self)

    # For debugging
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

    # For debugging
    def __str__(self):
        return f"{self.instructions}"

    class Instruction:
        # Instruction constructor
        def __init__(self, address=None, opcode=None, order=None):
            self.args       : list  = []
            self._address   : int   = address
            self._opcode    : str   = opcode
            self._order     : int   = order

        # Get instruction address
        # @return Instruction address
        def get_address(self):
            return self._address

        # Get instruction opcode
        # @return Instruction opcode
        def get_opcode(self):
            return self._opcode

        # Get instruction order
        # @return Instruction order
        def get_order(self):
            return self._order
        
        # Add argument to instruction
        # @param arg Argument to add
        def add_arg(self, arg, index=None):
            if arg is None:
                return
            if index is not None:
                self.args.insert(index-1, arg)
            else:
                self.args.append(arg)

        # Get argument from instruction
        # @param index Index of argument
        # @return Argument if exists, None otherwise
        def get_arg(self, index):
            if index < len(self.args):
                return self.args[index]
            return None

        # Execute instruction
        # @param program Program object
        def execute(self, program):
            # Maps opcode to specific instruction child class
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
            # Calls execute method of specific instruction child class
            opcode_to_class[self.get_opcode()].execute(self,program)

        class Argument:
            # Argument constructor
            def __init__(self, type=None, value=None):
                self._type : str = type
                match self._type:
                    case "int":
                        self._value : int   = set_int(value)
                    case "bool":
                        self._value : bool  = True if value == "true" else False
                    case "nil":
                        self._value : None  = None
                    case _:
                        self._value : str   = replace_escaped_chars(value)

            # Get argument type
            # @return Argument type
            def get_type(self):
                return self._type

            # Get frame type of argument
            # @return Frame type of argument
            # @note Only returns something when argument is variable
            def get_frame_type(self):
                if self._type == "var":
                    return self._value[:2]

            # Get argument value
            # @return Argument value
            def get_value(self):
                if self._type == "var":
                    return self._value[3:]
                else:
                    return self._value

            # For debugging
            def __str__(self):
                return f"{self._type} {self._value}"

    class Move(Instruction):
        # Execute MOVE instruction
        # @param program Program object
        def execute(self, program):
            temp_var = Program.Frame.Var()

            # Store argument type and value to temp variable
            arg = self.get_arg(1)
            match arg.get_type():
                case "var":
                    frame = check_frame_both(self, program, 1)
                    temp_var.set_type(frame.get_var(arg.get_value()).get_type())
                    temp_var.set_value(frame.get_var(arg.get_value()).get_value())
                case "int":
                    temp_var.set_type(arg.get_type())
                    temp_var.set_value(int(arg.get_value()))
                case "bool":
                    temp_var.set_type(arg.get_type())
                    temp_var.set_value(bool(arg.get_value()))
                case "string":
                    temp_var.set_type(arg.get_type())
                    temp_var.set_value(replace_escaped_chars(str(arg.get_value())))
                case "nil":
                    temp_var.set_type(arg.get_type())
                    temp_var.set_value(None)

            # Check if variable is declared and setting value
            frame = check_frame_declare(self, program, 0)
            frame.set_var(self.get_arg(0).get_value(), temp_var)
            program.set_pc(program.get_pc() + 1)
        
    class Not(Instruction):
        # Execute NOT instruction
        # @param program Program object
        def execute(self, program):
            # Check argument
            value = check_selected_type_arg(self, program, 1, "bool")
            # Check if variable is declared and setting value
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_value()).set_type("bool")
            frame.get_var(self.get_arg(0).get_value()).set_value(not value)
            program.set_pc(program.get_pc() + 1)
        
    class Int2char(Instruction):
        # Execute INT2CHAR instruction
        # @param program Program object
        def execute(self, program):
            # Check argument
            value = check_selected_type_arg(self, program, 1, "int")
            # Check if variable is declared and setting value
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_value()).set_type("string")
            try:
                frame.get_var(self.get_arg(0).get_value()).set_value(chr(value))
            except ValueError:
                print_error(self, "Wrong value of variable", 58)
            program.set_pc(program.get_pc() + 1)
        
    class Strlen(Instruction):
        # Execute STRLEN instruction
        # @param program Program object
        def execute(self, program):
            # Check argument
            value = check_selected_type_arg(self, program, 1, "string")
            # Check if variable is declared and setting value
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_value()).set_type("int")
            frame.get_var(self.get_arg(0).get_value()).set_value(len(value))
            program.set_pc(program.get_pc() + 1)
        
    class Type(Instruction):
        # Execute TYPE instruction
        # @param program Program object
        def execute(self, program):
            # Check argument
            arg = self.get_arg(1)
            if arg.get_type() == "var":
                frame = check_frame_declare(self, program, 1)
                if frame.get_var(arg.get_value()).get_value() != None:
                    type = frame.get_var(arg.get_value()).get_type()
                elif frame.get_var(arg.get_value()).get_type() == "var":
                    type = ""
                else:
                    type = frame.get_var(arg.get_value()).get_type()

            else:
                type = arg.get_type()
            # Check if variable is declared and setting value
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_value()).set_type("string")
            frame.get_var(self.get_arg(0).get_value()).set_value(str(type))
            program.set_pc(program.get_pc() + 1)

    class Createframe(Instruction):
        # Execute CREATEFRAME instruction
        # @param program Program object
        def execute(self, program):
            # Create new temp frame
            program.set_tf(program.Frame(TypeFrame.TEMP))
            program.set_pc(program.get_pc() + 1)
    
    class Pushframe(Instruction):
        # Execute PUSHFRAME instruction
        # @param program Program object
        def execute(self, program):
            # Push temp frame to local frame stack
            if program.tf() is None:
                print_error(self, "Temp frame not initialized", 55)
            program.push_stack(program.tf(), TypeStack.FRAME)
            program.set_tf(None)
            program.set_pc(program.get_pc() + 1)
        
    class Popframe(Instruction):
        def execute(self, program):
            # Pop local frame to temp frame
            if program.lf() is None:
                print_error(self, "Local frame not initialized", 55)
            program.set_tf(program.lf())
            program.pop_stack(TypeStack.FRAME)
            program.set_pc(program.get_pc() + 1)
        
    class Return(Instruction):
        # Execute RETURN instruction
        # @param program Program object
        def execute(self, program):
            # Pop call stack and set program counter
            if program.top_stack(TypeStack.CALL) is None:
                print_error(self, "Call stack is empty", 56)
            program.set_pc(program.pop_stack(TypeStack.CALL))
        
    class Break(Instruction):
        # Execute BREAK instruction
        # @param program Program object
        def execute(self, program):
            print("Program is on line: ", program.get_pc()+1, file=sys.stderr)
            program.print_frames()
            program.set_pc(program.get_pc() + 1)

    class Defvar(Instruction): 
        # Execute DEFVAR instruction
        # @param program Program object
        def execute(self, program):
            # Check frame of argument
            frame_dict = {"GF": program.gf, "LF": program.lf, "TF": program.tf}
            frame_name = self.get_arg(0).get_frame_type()
            if frame_name not in frame_dict:
                print_error(self, "Invalid frame", 55)
            # Check if frame is initialized
            frame = frame_dict.get(frame_name)()
            if frame is None and frame_name != "GF":
                print_error(self, f"{frame_name} not initialized", 55)
            # Check if variable already exists and add it to frame
            check_var_exists(self, frame, 0)
            frame.add_var(self.get_arg(0).get_value(), "var")
            program.set_pc(program.get_pc() + 1)

    class Pops(Instruction):
        # Execute POPS instruction
        # @param program Program object
        def execute(self, program):
            # Check if variable is declared in frame
            frame = check_frame_declare(self, program, 0)
            var = frame.get_var(self.get_arg(0).get_value())
            if program.top_stack(TypeStack.DATA) is None:
                print_error(self, "Data stack is empty", 56)
            # Set type of variable
            var.set_type(program.top_stack(TypeStack.DATA).get_type())
            # Pop data stack and set value of variable
            if program.top_stack(TypeStack.DATA).get_type() == "var":
                var.set_value(program.pop_stack(TypeStack.DATA).get_value())
            else:
                var.set_value(program.pop_stack(TypeStack.DATA).get_value())
            program.set_pc(program.get_pc() + 1)
        
    class Call(Instruction):
        # Execute CALL instruction
        # @param program Program object
        def execute(self, program):
            arg = self.get_arg(0)
            # Check if argument is label and if it exists
            if arg.get_type() != "label" or program.get_label_frame().get_var(arg.get_value()) is None:
                print_error(self, "Invalid label", 52)
            # Saving address of next instruction to call stack and setting pc to label address
            program.push_stack(program.get_pc()+1, TypeStack.CALL)
            program.set_pc(program.get_label_frame().get_var(arg.get_value()).get_value())
    
    class Label(Instruction):
        # Execute LABEL instruction
        # @param program Program object
        def execute(self, program):
            # Does nothing but is needed as point of jump
            program.set_pc(program.get_pc() + 1)

    class Jump(Instruction):
        # Execute JUMP instruction
        # @param program Program object
        def execute(self, program):
            arg = self.get_arg(0)
            # Check if label exists
            if arg.get_type() != "label" or program.get_label_frame().get_var(arg.get_value()) is None:
                print_error(self, "Invalid label", 52)
            program.set_pc(program.get_label_frame().get_var(arg.get_value()).get_value())
        
    class Pushs(Instruction):
        # Execute PUSHS instruction
        # @param program Program object
        def execute(self, program):
            arg = self.get_arg(0)
            # Check if argument is variable or constant and push it to data stack
            if arg.get_type() == "var":
                frame = check_frame_both(self, program, 0)
                program.push_stack(frame.get_var(arg.get_value()), TypeStack.DATA)
            else:
                program.push_stack(arg, TypeStack.DATA)
            program.set_pc(program.get_pc() + 1)
        
    class Write(Instruction):
        # Execute WRITE instruction
        # @param program Program object
        def execute(self, program):
            arg = self.get_arg(0)
            # Check if argument is variable or constant and print it
            if arg.get_type() == "var":
                frame = check_frame_both(self, program, 0)
                var = frame.get_var(arg.get_value())
                if var.get_type() == "bool":
                    print("true" if var.get_value() else "false", end='')
                elif var.get_type() == "nil":
                    print("", end='')
                elif var.get_type() == "string":
                    print(replace_escaped_chars(var.get_value()), end='')
                else:
                    print(var.get_value(), end='')
            elif arg.get_type() == "bool":
                print("true" if arg.get_value() else "false", end='')
            elif arg.get_type() == "nil":
                print("", end='')
            elif arg.get_type() == "string":
                print(replace_escaped_chars(arg.get_value()), end='')
            else:
                print(arg.get_value(), end='')
            program.set_pc(program.get_pc() + 1)

    class Exit(Instruction):
        # Execute EXIT instruction
        # @param program Program object
        def execute(self, program):
            # Check if argument is variable or constant
            arg_val = check_selected_type_arg(self, program, 0, "int")
            # Check if exit code is in range
            if not 0 <= int(arg_val) <= 49:
                print_error(self, "Wrong exit code", 57)
            exit(int(arg_val))

    class Dprint(Instruction):
        # Execute DPRINT instruction
        # @param program Program object
        def execute(self, program):
            arg_type = self.get_arg(0).get_type()
            # Check if argument is variable or constant and print it to stderr
            if arg_type == "var":
                frame = check_frame_both(self, program, 0)
                var = frame.get_var(self.get_arg(0).get_value())
                if var.get_type() == "bool":
                    print("true" if var.get_value() else "false", file=sys.stderr, end='')
                else:
                    print(var.get_value(), file=sys.stderr, end='')
            elif arg_type == "bool":
                print("true" if self.get_arg(0).get_value() else "false", file=sys.stderr, end='')
            elif arg_type == "nil":
                print("", file=sys.stderr, end='')
            else:
                print(self.get_arg(0).get_value(), file=sys.stderr, end='')
            program.set_pc(program.get_pc() + 1)

    class Add(Instruction):
        # Execute ADD instruction
        # @param program Program object
        def execute(self, program):
            # Check both arguments
            value2 = check_selected_type_arg(self, program, 2, "int")
            value1 = check_selected_type_arg(self, program, 1, "int")
            # Check if variable is declared and set its value to sum of arguments
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_value()).set_type("int")
            frame.get_var(self.get_arg(0).get_value()).set_value(int(value1 + value2))
            program.set_pc(program.get_pc() + 1)

    class Sub(Instruction):
        # Execute SUB instruction
        # @param program Program object
        def execute(self, program):
            # Check both arguments
            value2 = check_selected_type_arg(self, program, 2, "int")
            value1 = check_selected_type_arg(self, program, 1, "int")
            # Check if variable is declared and set its value to difference of arguments
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_value()).set_type("int")
            frame.get_var(self.get_arg(0).get_value()).set_value(int(value1 - value2))
            program.set_pc(program.get_pc() + 1)

    class Mul(Instruction):
        # Execute MUL instruction
        # @param program Program object
        def execute(self, program):
            # Check both arguments
            value2 = check_selected_type_arg(self, program, 2, "int")
            value1 = check_selected_type_arg(self, program, 1, "int")
            # Check if variable is declared and set its value to product of arguments
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_value()).set_type("int")
            frame.get_var(self.get_arg(0).get_value()).set_value(int(value1 * value2))
            program.set_pc(program.get_pc() + 1)

    class Idiv(Instruction):
        # Execute IDIV instruction
        # @param program Program object
        def execute(self, program):
            # Check both arguments
            value2 = check_selected_type_arg(self, program, 2, "int")
            if value2 == 0:
                print_error(self, "Division by zero", 57)
            value1 = check_selected_type_arg(self, program, 1, "int")
            # Check if variable is declared and set its value to quotient of arguments
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_value()).set_type("int")
            frame.get_var(self.get_arg(0).get_value()).set_value(int(value1 / value2))
            program.set_pc(program.get_pc() + 1)

    class Lt(Instruction):
        # Execute LT instruction
        # @param program Program object
        def execute(self, program):
            arg1_val = get_val(self, program, 1) 
            arg2_val = get_val(self, program, 2)
            type1 = get_typ(self, program, 1)
            type2 = get_typ(self, program, 2)
            if type1 == "nil" or type2 == "nil":
                print_error(self, "Wrong type of argument, argument can't be nil", 53)
            if type1 != type2:
                print_error(self, "Arguments are not the same type", 53)
            # Check if variable is declared and set its value to True if arg1 < arg2
            frame = check_frame_declare(self, program, 0)
            result_var = frame.get_var(self.get_arg(0).get_value())
            result_var.set_type("bool")
            result_var.set_value(arg1_val < arg2_val)
            program.set_pc(program.get_pc() + 1)

    class Gt(Instruction):
        # Execute GT instruction
        # @param program Program object
        def execute(self, program):
            arg1_val = get_val(self, program, 1) 
            arg2_val = get_val(self, program, 2)
            type1 = get_typ(self, program, 1)
            type2 = get_typ(self, program, 2)
            if type1 == "nil" or type2 == "nil":
                print_error(self, "Wrong type of argument, argument can't be nil", 53)
            if type1 != type2:
                print_error(self, "Arguments are not the same type", 53)
            # Check if variable is declared and set its value to True if arg1 > arg2
            frame = check_frame_declare(self, program, 0)
            result_var = frame.get_var(self.get_arg(0).get_value())
            result_var.set_type("bool")
            result_var.set_value(arg1_val > arg2_val)
            program.set_pc(program.get_pc() + 1)

    class Eq(Instruction):
        # Execute EQ instruction
        # @param program Program object
        def execute(self, program):
            arg1_val = get_val(self, program, 1) 
            arg2_val = get_val(self, program, 2)
            type1 = get_typ(self, program, 1)
            type2 = get_typ(self, program, 2)
            if type1 == "nil" or type2 == "nil":
                pass
            elif type1 != type2:
                print_error(self, "Arguments are not the same type and neither is nil", 53)
            # Check if variable is declared and set its value to True if arg1 == arg2
            frame = check_frame_declare(self, program, 0)
            result_var = frame.get_var(self.get_arg(0).get_value())
            result_var.set_type("bool")
            result_var.set_value(arg1_val == arg2_val)
            program.set_pc(program.get_pc() + 1)

    class And(Instruction):
        # Execute AND instruction
        # @param program Program object
        def execute(self, program):
            # Check both arguments
            value2 = check_selected_type_arg(self, program, 2, "bool")
            value1 = check_selected_type_arg(self, program, 1, "bool")
            # Check if variable is declared and set its value to logical AND of arguments
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_value()).set_type("bool")
            frame.get_var(self.get_arg(0).get_value()).set_value(value1 and value2)
            program.set_pc(program.get_pc() + 1)

    class Or(Instruction):
        # Execute OR instruction
        # @param program Program object
        def execute(self, program):
            # Check both arguments
            value2 = check_selected_type_arg(self, program, 2, "bool")
            value1 = check_selected_type_arg(self, program, 1, "bool")
            # Check if variable is declared and set its value to logical OR of arguments
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_value()).set_type("bool")
            frame.get_var(self.get_arg(0).get_value()).set_value(value1 or value2)
            program.set_pc(program.get_pc() + 1)

    class Str2int(Instruction):
        # Execute STR2INT instruction
        # @param program Program object
        def execute(self, program):
            # check both arguments
            index = check_selected_type_arg(self, program, 2, "int")
            if index < 0:
                print_error(self, "Index value of index", 58)
            value = check_selected_type_arg(self, program, 1, "string")
            # Check if variable is declared and set its value to int value of char at index
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_value()).set_type("int")
            try:
                frame.get_var(self.get_arg(0).get_value()).set_value(ord(value[index]))
            except IndexError:
                print_error(self, "Index out of range", 58)
            except ValueError:
                print_error(self, "Invalid value of argument", 58)
            program.set_pc(program.get_pc() + 1)
            
    class Concat(Instruction):
        # Execute CONCAT instruction
        # @param program Program object
        def execute(self, program):
            # Check both arguments
            value2 = check_selected_type_arg(self, program, 2, "string")
            value1 = check_selected_type_arg(self, program, 1, "string")
            # Check if variable is declared and set its value to concatenation of arguments
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_value()).set_type("string")
            frame.get_var(self.get_arg(0).get_value()).set_value(value1 + value2)
            program.set_pc(program.get_pc() + 1)

    class Getchar(Instruction):
        # Execute GETCHAR instruction
        # @param program Program object
        def execute(self, program):
            # Check both arguments
            index = check_selected_type_arg(self, program, 2, "int")
            if index < 0:
                print_error(self, "Invalid value of index", 58)
            value = check_selected_type_arg(self, program, 1, "string")
            # Check if variable is declared and set its value to char at index
            frame = check_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_value()).set_type("string")
            try:
                frame.get_var(self.get_arg(0).get_value()).set_value(value[index])
            except IndexError:
                print_error(self, "Index out of range", 58)
            program.set_pc(program.get_pc() + 1)

    class Setchar(Instruction):
        # Execute SETCHAR instruction
        # @param program Program object
        def execute(self, program):
            # Check both arguments
            char = check_selected_type_arg(self, program, 2, "string")
            if char == "":
                print_error(self, "Empty character", 58)
            index = check_selected_type_arg(self, program, 1, "int")
            # Check if variable is declared and replaces character at index with char
            frame = check_frame_both(self, program, 0)
            arg_val = self.get_arg(0).get_value()
            if frame.get_var(arg_val).get_type() != "string":
                print_error(self, "Wrong type of argument, argument is not a string", 53)
            if len(frame.get_var(arg_val).get_value()) <= index or index < 0:
                print_error(self, "Index out of range", 58)
            try:
                frame.get_var(self.get_arg(0).get_value()).set_char(char, index)
            except IndexError:
                print_error(self, "Index out of range", 58)
            program.set_pc(program.get_pc() + 1)

    class Read(Instruction):
        # Execute READ instruction
        # @param program Program object
        def execute(self, program):
            # Check argument
            value = check_selected_type_arg(self, program, 1, "type")
            # Check if variable is declared and set its value to input based on type
            frame = check_frame_declare(self, program, 0)
            var = frame.get_var(self.get_arg(0).get_value())
            try:
                line = input.readline()
                if line == "":
                    var.set_type("nil")
                    var.set_value(None)
                elif line == "\n":
                    var.set_type("string")
                    var.set_value("")
                elif value == "int":
                    var.set_type("int")
                    var.set_value(int(line.strip()))
                elif value == "bool":
                    var.set_type("bool")
                    var.set_value(True) if line.strip().lower() == "true" else var.set_value(False)
                elif value == "string":
                    var.set_type("string")
                    var.set_value(replace_escaped_chars(line.strip()))
            except ValueError:
                var.set_type("nil")
                var.set_value(None)
            program.set_pc(program.get_pc() + 1)

    class Jumpifeq(Instruction):
        # Execute JUMPIFEQ instruction
        # @param program Program object
        def execute(self, program):
            # Check both arguments
            value2 = get_val(self, program, 2)
            value1 = get_val(self, program, 1) 
            type2 = get_typ(self, program, 2)
            type1 = get_typ(self, program, 1)
            if type1 == "nil" or type2 == "nil":
                pass
            elif type1 != type2:
                print_error(self, "Arguments are not the same type", 53)
            # Check if label is declared and set program counter to label address if values are equal
            arg = self.get_arg(0)
            if arg.get_type() != "label" or program.get_label_frame().get_var(arg.get_value()) is None:
                print_error(self, "Invalid label", 52)
            if value1 == value2:
                program.set_pc(program.get_label_frame().get_var(arg.get_value()).get_value())
            else:
                program.set_pc(program.get_pc() + 1)

    class Jumpifneq(Instruction):
        # Execute JUMPIFNEQ instruction
        # @param program Program object
        def execute(self, program):
            # Check both arguments
            value2 = get_val(self, program, 2)
            value1 = get_val(self, program, 1)
            type2 = get_typ(self, program, 2)
            type1 = get_typ(self, program, 1)
            if type1 == "nil" or type2 == "nil":
                pass
            elif type1 != type2:
                print_error(self, "Arguments are not the same type and neither is nil", 53)
            # Check if label is declared and set program counter to label address if values are not equal
            arg = self.get_arg(0)
            if arg.get_type() != "label" or program.get_label_frame().get_var(arg.get_value()) is None:
                print_error(self, "Invalid label", 52)
            if value1 != value2:
                program.set_pc(program.get_label_frame().get_var(arg.get_value()).get_value())
            else:
                program.set_pc(program.get_pc() + 1)

    class Frame:
        # Frame constructor
        def __init__(self,type):
            self.vars   : dict      = {}
            self._type  : TypeFrame = type

        # Add variable to frame
        # @param var_value Variable value
        # @param type Variable type
        def add_var(self, var_value, type=None):
            self.vars[var_value] = self.Var(type)

        # Get variable from frame
        # @param var_value Variable value
        # @return Variable object
        def get_var(self, var_value):
            if var_value in self.vars:
                return self.vars[var_value]
            return None

        # Set variable in frame
        # @param var_value Variable value
        # @param var Variable object
        def set_var(self, var_value, var):
            self.vars[var_value] = var
        
        # Print frame
        def print(self):
            for var in self.vars:
                print("-> type: " + self.vars[var].get_type() + ", [\"" + var + "\" : " + str(self.vars[var].get_value()) + "]")

        # for debugging
        def __str__(self):
            return f"{self.vars}"

        class Var:
            # Variable constructor
            def __init__(self, type=None, value=None):
                self._type  : str = type
                self._value       = value

            # Get variable type
            # @return Variable type
            def get_type(self):
                return self._type

            # Set variable type
            # @param type Variable type
            def set_type(self, type):
                self._type : str = type

            # Get frame type
            # @return Frame type
            def get_frame_type(self):
                return super()._type

            # Get variable value
            # @return Variable value
            def get_value(self):
                return self._value

            # Set variable value
            # @param value Variable value
            def set_value(self, value):
                self._value = value

            # Sets (replaces) character at index with char
            # @param char Character to be set
            # @param index Index of character to be replaced
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

# Types of stacks
class TypeStack(Enum):
    DATA = 0
    CALL = 1
    FRAME = 2

# Parsing script arguments
# @return tuple of xml_root and input data
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
        input = sys.stdin

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
            input = input_file
        else:
            print("ERROR: Input file doesn't exists", file=sys.stderr)
            exit(11)
    return (xml_root, input)

# Checks if given variable already exists
# @param instruction Instruction to be checked
# @param frame Frame of given variable
# @param arg_index Index of argument to be checked
def check_var_exists(instruction, frame, arg_index):
    if instruction.get_arg(arg_index).get_value() in frame.vars:
        print_error(instruction, "Variable already declared", 52)

# Checks if variable is declared
# @param instruction Instruction to be checked
# @param frame Frame of given variable
# @param arg_index Index of argument to be checked
def check_var_declaration(instruction, frame, arg_index):
    if instruction.get_arg(arg_index).get_value() not in frame.vars:
        print_error(instruction, "Variable not declared", 54)

# Checks if variable is defined
# @param instruction Instruction to be checked
# @param frame Frame of given variable
# @param arg_index Index of argument to be checked
def check_var_definition(instruction, frame, arg_index):
    if frame.vars[instruction.get_arg(arg_index).get_value()].get_type() == "nil":
        return
    if frame.vars[instruction.get_arg(arg_index).get_value()].get_value() is None:
        print_error(instruction, "Variable not defined", 56)

# Function looks for variable in given frame, checks if it is declared and returns given frame
# @param instruction Instruction to be checked
# @param program Program object
# @param arg_index Index of argument to be checked
# @return Frame of given variable
def check_frame_declare(instruction, program, arg_index):
    if instruction.get_arg(arg_index).get_frame_type() == "GF":
        check_var_declaration(instruction, program.gf(), arg_index)
        return program.gf()
    elif instruction.get_arg(arg_index).get_frame_type() == "LF":
        if program.lf() is None:
            print_error(instruction, "Local frame not initialized", 55)
        check_var_declaration(instruction, program.lf(), arg_index)
        return program.lf()
    if instruction.get_arg(arg_index).get_frame_type() == "TF":
        if program.tf() is None:
            print_error(instruction, "Temp frame not initialized", 55)
        check_var_declaration(instruction, program.tf(), arg_index)
        return program.tf()

# Function looks for variable in given frame, checks if it is declared and defined and returns given frame
# @param instruction Instruction to be checked
# @param program Program object
# @param arg_index Index of argument to be checked
# @return Frame of given variable
def check_frame_both(instruction, program, arg_index):
    if instruction.get_arg(arg_index).get_frame_type() == "GF":
        check_var_declaration(instruction, program.gf(), arg_index)
        check_var_definition(instruction, program.gf(), arg_index)
        return program.gf()
    elif instruction.get_arg(arg_index).get_frame_type() == "LF":
        if program.lf() is None:
            print_error(instruction, "Local frame not initialized", 55)
        check_var_declaration(instruction, program.lf(), arg_index)
        check_var_definition(instruction, program.lf(), arg_index)
        return program.lf()
    if instruction.get_arg(arg_index).get_frame_type() == "TF":
        if program.tf() is None:
            print_error(instruction, "Temp frame not initialized", 55)
        check_var_declaration(instruction, program.tf(), arg_index)
        check_var_definition(instruction, program.tf(), arg_index)
        return program.tf()

# Prints error message
# @param instruction Instruction where error occured
# @param error_msg Error message
# @param error_code Error code
def print_error(instruction, error_msg, error_code):
    print("ERROR on line: " + str(instruction.get_address()+1), file=sys.stderr)
    print("ERROR: " + error_msg, file=sys.stderr)
    exit(error_code)

# Function checks if argument for selected type is correct and returns its value
# @param program Program object
# @param arg_index Index of argument
# @param type Type of argument
# @return Value of argument
def check_selected_type_arg(self, program, arg_index, type):
    if self.get_arg(arg_index).get_type() == "var":
        frame = check_frame_both(self, program, arg_index)
        if frame.get_var(self.get_arg(arg_index).get_value()).get_type() != type:
            print_error(self, "Wrong type of argument", 53)
        return frame.get_var(self.get_arg(arg_index).get_value()).get_value()
    elif self.get_arg(arg_index).get_type() != type:
        print_error(self, "Wrong type of argument", 53)
    return self.get_arg(arg_index).get_value()

# Function checks if argument is variable or symbol and returns its type
# @param instr Instruction object
# @param program Program object
# @param arg_index Index of argument
# @return Type of argument
def get_typ(instr, program, arg_index):
    arg = instr.get_arg(arg_index)
    if arg.get_type() == "var":
        frame = check_frame_both(instr, program, arg_index)
        return frame.get_var(arg.get_value()).get_type()
    return arg.get_type()

# Function checks if argument is variable or symbol and returns its value
# @param instr Instruction object
# @param program Program object
# @param arg_index Index of argument
# @return Value of argument
def get_val(instr, program, arg_index):
    arg = instr.get_arg(arg_index)
    if arg.get_type() == "var":
        frame = check_frame_both(instr, program, arg_index)
        return frame.get_var(arg.get_value()).get_value()
    return arg.get_value()

# Replaces escaped characters (\xyz) in string
# @param string String to be replaced
# @return String with replaced characters 
def replace_escaped_chars(string):
    idx = string.find("\\")
    if idx == -1:
        return string
    while(idx != -1):
        if len(string) - idx < 4:
            idx = string.find("\\", idx+1)
            continue
        if not string[idx+1].isdigit() or not string[idx+2].isdigit() or not string[idx+3].isdigit():
            idx = string.find("\\", idx+1)
            continue
        try:
            string = string[:idx] + chr(int(string[idx+1:idx+4])) + string[idx+4:]
            idx = string.find("\\", idx+1)
        except ValueError:
            print("ERROR: Invalid escape sequence", file=sys.stderr)
            exit(58)
    return string

# Function sets integer value based on format of given argument
# @param value String to be converted to integer
# @return Integer value
def set_int(value):
    if re.match(r"^[+-]?0$", value):
        return int(value, 10)
    if re.match(r"^[+-]?(0x|0X)[\da-fA-F]+(_[\da-fA-F]+)*$", value):
        return int(value, 16)
    elif 'o' in value or 'O' in value:
        if re.match(r"^[+-]?0(o|O)?[0-7]+(_[0-7]+)*$", value):
            return int(value, 8)
    elif re.match(r"^[+-]?0+[0-7]*(_[0-7]+)*$", value):
        # we remove leading zeros
        value = re.sub(r"^0+", "", value)
        return int(value, 8)
    elif re.match(r"^[+-]?[1-9][\d]*(_[\d]+)*$", value):
        return int(value, 10)
    
# Generates program structure from XML to objects (classes)
# @param xml_root Root of XML tree
# @return Program object
def gen_program(xml_root):
    program = Program()
    address = 0
    for instr in xml_root:
        instr_obj = program.Instruction(address, instr.attrib["opcode"].upper(), instr.attrib["order"])
        for arg in instr:
            arg.text = "" if arg.text is None else arg.text.strip()
            arg_obj = instr_obj.Argument(arg.attrib["type"], arg.text)
            instr_obj.add_arg(arg_obj, int(arg.tag[-1]))
        program.add_instr(instr_obj)
        # Generates labels
        if instr_obj.get_opcode() == "LABEL":
            gen_label(instr_obj, program)
        address += 1
    return program

# Generates labels in the first iteration of program
# @param instr Instruction object
# @param program Program object
def gen_label(instr, program):
    arg = instr.get_arg(0)
    if arg.get_type() != "label" or program.get_label_frame().get_var(arg.get_value()) is not None:
        print_error(instr, "Invalid label", 52)
    program.get_label_frame().add_var(arg.get_value(), "label")
    program.get_label_frame().get_var(arg.get_value()).set_value(instr.get_address()+1)

# Checks if order attributes are without duplicates
# @param program Program object
def check_order_attribute(program):
    dup_list = []
    for instr in program.instructions:
        if instr.get_order() in dup_list:
            print("ERROR on line: " + str(instr.get_address()+1), file=sys.stderr)
            print("ERROR: Duplicate order attribute", file=sys.stderr)
            exit(32)
        dup_list.append(instr.get_order())

# Sorts instructions by order attribute
# @param program Program object
# @return Program object
def sort_by_order(program):
    program.instructions.sort(key=lambda instr: int(instr.get_order()))
    return program

# Main function
if __name__ == "__main__":
    xml_root, input = parse_sc_args()
    check_xml.check_xml(xml_root)
    prg = gen_program(xml_root)
    check_order_attribute(prg)
    prg = sort_by_order(prg)
    prg.run()
    exit(0)