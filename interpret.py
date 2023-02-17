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
        return self._stack.pop()
    
    def top(self):
        return self._stack[-1]
    
    def empty(self):
        self._stack.clear()

class Program:
    def  __init__(self):
        self.instructions = []
        self._data_stack = Stack()
        self._frame_stack = Stack()
        self._call_stack = Stack() #
        self._global_frame = self.Frame(TypeFrame.GLOBAL) 
        self._temp_frame = None
        self._program_counter = 0

    # add instruction to program
    def add_instr(self, instr):
        self.instructions.append(instr)

    # get instruction by order
    def get_instr(self, order):
        for instr in self.instructions:
            if instr.order == order:
                return instr
        return None

    # get global frame
    def gf(self):
        return self._global_frame

    # get local frame
    def lf(self):
        if len(self._frame_stack._stack) > 0:
            return self._frame_stack.top()
    
    # set local frame
    def set_lf(self, frame):
        self._frame_stack.push(frame)

    # pop local frame
    def pop_lf(self):
        if len(self._frame_stack._stack) > 0:
            self._frame_stack.pop() 

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
    def inc_pc(self):
        self._program_counter += 1

    # for debugging
    def print_frames(self):
        print("[GLOBAL FRAME]")
        self.gf().print()
        print("[LOCAL FRAME]")
        if self.lf() is not None:
            self.lf().print()
        else:
            print("Not initialized")
        print("[TEMP FRAME]")
        if self.tf() is not None:
            self.tf().print()
        else:
            print("Not initialized")

    # for debugging
    def __str__(self):
        return f"{self.instructions}"

    class Instruction:
        def __init__(self, opcode=None, order=None):
            self.opcode: str = opcode
            self.order: int = order
            self.args = []
        
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
            program.inc_pc()
            return opcode_to_class[self.opcode].execute(self,program)

        class Argument:
            def __init__(self, type=None, value=None):
                self.type: str = type
                if self.type == "var":
                    self.value: str = value
                elif self.type == "int":
                    if re.match(r"^[-+]?[1-9][0-9]*$", value):
                       self.value: int = int(value) 
                    elif re.match(r"^[+-]?(0x|0X)?[0-9]+$", value):
                        self.value: int = int(value, 16)
                    elif re.match(r"^[+-]?0[0-7]+$", value):
                        self.value: int = int(value, 8)
                elif self.type == "bool":
                    if value == "true":
                        self.value: bool = True
                    else:
                        self.value: bool = False
                elif self.type == "string":
                    self.value: str = value
                else:
                    self.value = ""

            def get_type(self):
                return self.type

            # only returns something when argument is variable
            def get_frame(self):
                if self.type == "var":
                    return self.value[:2]

            def get_arg_name(self):
                if self.type == "var":
                    return self.value[3:]
                else:
                    return self.value

            # for debugging
            def __str__(self):
                return f"{self.type} {self.value}"

    class Move(Instruction):
        def execute(self, program):
            temp_var = Program.Frame.Var()
            # Checking symbol
            if self.get_arg(1).get_type() == "var":
                frame = choose_frame_both(self, program, 1)
                temp_var.set_value(frame.get_var(self.get_arg(1).get_arg_name()))
            elif self.get_arg(1).get_type() == "int":
                temp_var.set_value(int(self.get_arg(1).get_arg_name()))
            elif self.get_arg(1).get_type() == "bool":
                temp_var.set_value(bool(self.get_arg(1).get_arg_name()))
            elif self.get_arg(1).get_type() == "string":
                temp_var.set_value(str(self.get_arg(1).get_arg_name()))
            elif self.get_arg(1).get_type() == "nil":
                temp_var.set_value(None)
                        
            temp_var.set_type(self.get_arg(1).get_type())
            # Checking variable
            frame = choose_frame_declare(self, program, 0)
            frame.set_var(self.get_arg(0).get_arg_name(), temp_var)
        
    class Not(Instruction):
        def execute(self, program):
            # Checking symbol
            if self.get_arg(1).get_type() == "var":
                frame = choose_frame_both(self, program, 1)
                if frame.get_var(self.get_arg(1).get_arg_name()).get_type() == "bool":
                    value = frame.get_var(self.get_arg(1).get_arg_name()).get_value()
                else:
                    print("ERROR: Wrong type of variable", file=sys.stderr)
                    exit(53)
            elif self.get_arg(1).get_type() == "bool":
                value = self.get_arg(1).get_arg_name()
            else:
                print("ERROR: Wrong type of variable", file=sys.stderr)
                exit(53)
            # Checking variable and setting value, (*) Maybe need to check type of variable? !!!
            frame = choose_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_name()).set_type("bool")
            frame.get_var(self.get_arg(0).get_arg_name()).set_value(not value)
        
    class Int2char(Instruction):
        def execute(self, program):
            pass
        
    class Strlen(Instruction):
        def execute(self, program):
            pass
        
    class Type(Instruction):
        def execute(self, program):
            # Checking symbol and getting its type
            type = ""
            if self.get_arg(1).get_type() == "var":
                frame = choose_frame_declare(self, program, 1)
                if frame.vars[self.get_arg(1).get_arg_name()].get_value() is not None:
                    type = frame.get_var(self.get_arg(1).get_arg_name()).get_type()
            else:
                type = self.get_arg(1).get_type()
            # Checking variable
            frame = choose_frame_declare(self, program, 0)
            frame.get_var(self.get_arg(0).get_arg_name()).set_value(str(type))

    class Createframe(Instruction):
        def execute(self, program):
            program.set_tf(program.Frame(TypeFrame.TEMP))
    
    class Pushframe(Instruction):
        def execute(self, program):
            if program.tf() is None:
                print("ERROR: Temp frame not initialized")
                exit(55)
            program.set_lf(program.tf())
            program.set_tf(None)
        
    class Popframe(Instruction):
        def execute(self, program):
            if program.lf() is None:
                print("ERROR: Local frame not initialized")
                exit(55)
            program.set_tf(program.lf())
            program.pop_lf()
        
    class Return(Instruction):
        def execute(self, program):
            pass
        
    class Break(Instruction):
        def execute(self, program):
            pass

    class Defvar(Instruction): #defvar type var, also add enums for vartype, argtype 
        def execute(self, program):
            if self.get_arg(0).get_frame() == "GF":
                check_var_exists(self.get_arg(0).get_arg_name(), program.gf())
                program.gf().add_var(self.get_arg(0).get_arg_name(), self.get_arg(0).get_type())
            elif self.get_arg(0).get_frame() == "LF":
                if program.lf() is None:
                    print("ERROR: Local frame not initialized")
                    exit(55)
                check_var_exists(self.get_arg(0).get_arg_name(), program.lf())
                program.lf().add_var(self.get_arg(0).get_arg_name(), self.get_arg(0).get_type())
            elif self.get_arg(0).get_frame() == "TF":
                if program.tf() is None:
                    print("ERROR: Temp frame not initialized")
                    exit(55)
                check_var_exists(self.get_arg(0).get_arg_name(), program.tf())
                program.tf().add_var(self.get_arg(0).get_arg_name(), self.get_arg(0).get_type())

    class Pops(Instruction):
        def execute(self, program):
            pass
        
    class Call(Instruction):
        def execute(self, program):
            pass
    
    class Label(Instruction):
        def execute(self, program):
            pass

    class Jump(Instruction):
        def execute(self, program):
            pass
        
    class Pushs(Instruction):
        def execute(self, program):
            pass
        
    class Write(Instruction):
        def execute(self, program):
            if self.get_arg(0).get_type() == "var":
                frame = choose_frame_both(self, program, 0)
                if frame.get_var(self.get_arg(0).get_arg_name()).get_type() == "bool":
                    if frame.get_var(self.get_arg(0).get_arg_name()).get_value():
                        print("true", end='')
                    else:
                        print("false", end='')
                else:
                    print(frame.get_var(self.get_arg(0).get_arg_name()).get_value(), end='')
            elif self.get_arg(0).get_type() == "bool":
                if self.get_arg(0).get_arg_name():
                    print("true", end='')
                else:
                    print("false", end='')
            elif self.get_arg(0).get_type() == "nil":
                print("", end='')
            else:
                print(self.get_arg(0).get_arg_name(), end='')

    class Exit(Instruction):
        def execute(self, program):
            if self.get_arg(0).get_type() == "var":
                frame = choose_frame_both(self, program, 0)
                exit(frame.get_var(self.get_arg(0).get_arg_name()).get_value())
            elif self.get_arg(0).get_type() == "int":
                if int(self.get_arg(0).get_arg_name()) >= 0 and int(self.get_arg(0).get_arg_name()) <= 49:
                    exit(int(self.get_arg(0).get_arg_name()))
                else:
                    print("ERROR: Wrong exit code")
                    exit(57)
            else:
                print("ERROR: Wrong type of argument")
                exit(53)

    class Dprint(Instruction):
        def execute(self, program):
            pass

    class Add(Instruction):
        def execute(self, program):
            pass

    class Sub(Instruction):
        def execute(self, program):
            pass

    class Mul(Instruction):
        def execute(self, program):
            pass

    class Idiv(Instruction):
        def execute(self, program):
            pass

    class Lt(Instruction):
        def execute(self, program):
            pass

    class Gt(Instruction):
        def execute(self, program):
            pass

    class Eq(Instruction):
        def execute(self, program):
            pass

    class And(Instruction):
        def execute(self, program):
            pass

    class Or(Instruction):
        def execute(self, program):
            pass

    class Str2int(Instruction):
        def execute(self, program):
            pass

    class Concat(Instruction):
        def execute(self, program):
            pass

    class Getchar(Instruction):
        def execute(self, program):
            pass

    class Setchar(Instruction):
        def execute(self, program):
            pass

    class Read(Instruction):
        def execute(self, program):
            pass

    class Jumpifeq(Instruction):
        def execute(self, program):
            pass

    class Jumpifneq(Instruction):
        def execute(self, program):
            pass

    class Frame:
        def __init__(self,type):
            self.vars = {}
            self.type: TypeFrame = type

        def add_var(self, var_name, type=None):
            self.vars[var_name] = self.Var(type)

        def get_var(self, var_name):
            return self.vars[var_name]

        def set_var(self, var_name, var):
            self.vars[var_name] = var
        
        def print(self):
            for var in self.vars:
                print(var, self.vars[var])

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

            def __str__(self):
                return f"{self._value}"

class TypeFrame(Enum):
    GLOBAL = 0
    LOCAL = 1
    TEMP = 2

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
def check_var_exists(var_name, frame):
    if var_name in frame.vars:
        print("ERROR: Variable already declared", file=sys.stderr)
        exit(52)

# Checks if variable is declared
def check_var_declaration(instruction, frame, arg_index):
    if instruction.get_arg(arg_index).get_arg_name() not in frame.vars:
        print("ERROR: Variable not declared", file=sys.stderr)
        exit(54)

# Checks if variable is defined
def check_var_definition(instruction, frame, arg_index):
    if frame.vars[instruction.get_arg(arg_index).get_arg_name()].get_value() is None:
        print("ERROR: Variable not defined", file=sys.stderr)
        exit(56)

# Function looks for variable in given frame, checks if it is declared and returns given frame
def choose_frame_declare(instruction, program, arg_index):
    if instruction.get_arg(arg_index).get_frame() == "GF":
        check_var_declaration(instruction, program.gf(), arg_index)
        return program.gf()
    elif instruction.get_arg(arg_index).get_frame() == "LF":
        if program.lf() is None:
            print("ERROR: Local frame not initialized")
            exit(55)
        check_var_declaration(instruction, program.lf(), arg_index)
        return program.lf()
    if instruction.get_arg(arg_index).get_frame() == "TF":
        if program.tf() is None:
            print("ERROR: Temp frame not initialized")
            exit(55)
        check_var_declaration(instruction, program.tf(), arg_index)
        return program.tf()

# Function looks for variable in given frame, checks if it is declared and defined and returns given frame
def choose_frame_both(instruction, program, arg_index):
    if instruction.get_arg(arg_index).get_frame() == "GF":
        check_var_declaration(instruction, program.gf(), arg_index)
        check_var_definition(instruction, program.gf(), arg_index)
        return program.gf()
    elif instruction.get_arg(arg_index).get_frame() == "LF":
        if program.lf() is None:
            print("ERROR: Local frame not initialized")
            exit(55)
        check_var_declaration(instruction, program.lf(), arg_index)
        check_var_definition(instruction, program.lf(), arg_index)
        return program.lf()
    if instruction.get_arg(arg_index).get_frame() == "TF":
        if program.tf() is None:
            print("ERROR: Temp frame not initialized")
            exit(55)
        check_var_declaration(instruction, program.tf(), arg_index)
        check_var_definition(instruction, program.tf(), arg_index)
        return program.tf()

# Generates program structure from XML
def gen_program(xml_root):
    program = Program()
    for instr in xml_root:
        instr_obj = Program.Instruction(instr.attrib["opcode"], instr.attrib["order"])
        for arg in instr:
            if arg.text is None: 
                arg.text = ""
            arg_obj = Program.Instruction.Argument(arg.attrib["type"], arg.text)
            instr_obj.add_arg(arg_obj)
        program.add_instr(instr_obj)
    return program

# Checks if order attributes are without duplicates
def check_order_attribute(program):
    dup_list = []
    for instr in program.instructions:
        if instr.order in dup_list:
            print("ERROR: Duplicate order attribute", file=sys.stderr)
            exit(32)
        dup_list.append(instr.order)

# Sorts instructions by order attribute
def sort_by_order(program):
    program.instructions.sort(key=lambda instr: int(instr.order))
    return program

# Prints program
def print_program():
    for instr in prg.instructions:
        print(instr.order+": ",instr.opcode)
        for arg in instr.args:
            print(arg.type, arg.value)

# change this to normal for loop and loop through addresses of instructions
def run_program(program):
    for instruction in program.instructions:
        instruction.execute(program)

    #program.print_frames()

if __name__ == "__main__":
    xml_root, input = parse_sc_args()
    check_xml.check_xml(xml_root)
    gen_program(xml_root)
    prg = gen_program(xml_root)
    check_order_attribute(prg)
    prg = sort_by_order(prg)
    #print_program()
    run_program(prg)
    exit(0)