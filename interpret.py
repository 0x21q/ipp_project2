#!/usr/bin/python3.10
import argparse, re, os.path, sys
import xml.etree.ElementTree as ET
from collections import deque
from enum import Enum

# Stack implementation using deque
class Stack:
    def __init__(self):
        self.stack = deque()
    
    def push(self, data):
        self.stack.append(data)

    def pop(self):
        return self.stack.pop()
    
    def top(self):
        return self.stack[-1]
    
    def empty(self):
        self.stack.clear()

class Program:
    def  __init__(self):
        self.instructions = []
        self.data_stack = Stack()
        self.frame_stack = Stack()
        self.global_frame = self.Frame(TypeFrame.GLOBAL) 
        self.local_frame = None
        self.temp_frame = None

    # maybe put instructior of Instruction class inside this method
    def add_instr(self, instr):
        self.instructions.append(instr)

    def get_instr(self, order):
        for instr in self.instructions:
            if instr.order == order:
                return instr
        return None

    # for debugging
    def print_frames(self):
        print("[GLOBAL FRAME]")
        self.global_frame.print()
        print("[LOCAL FRAME]")
        if self.local_frame is not None:
            self.local_frame.print()
        else:
            print("Not initialized")
        print("[TEMP FRAME]")
        if self.temp_frame is not None:
            self.temp_frame.print()
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

        def run(self, program):
            match self.opcode:
                case "MOVE":
                    temp_var = Program.Frame.Var()
                    # Checking symbol
                    match self.get_arg(1).get_type():
                        case "var":
                            match self.get_arg(1).get_frame():
                                case "GF":
                                    check_var_declaration(self, program.global_frame, 1)
                                    check_var_definition(self, program.global_frame, 1)
                                    temp_var.set_value(program.global_frame.vars[self.get_arg(1).get_arg_name()])
                                case "LF":
                                    # need change probably
                                    check_var_declaration(self, program.global_frame, 1)
                                    check_var_definition(self, program.local_frame, 1)
                                    temp_var.set_value(program.global_frame.vars[self.get_arg(1).get_arg_name()])
                                case "TF": # maybe shouldnt even be here, needs check !!!
                                    # need change probably
                                    check_var_declaration(self, program.global_frame, 1)
                                    check_var_definition(self, program.temp_frame, 1)
                                    temp_var = program.temp_frame.vars[self.get_arg(1).get_var_name()]
                                    temp_var.set_value(program.global_frame.vars[self.get_arg(1).get_arg_name()])
                        case "int":
                            temp_var.set_value(int(self.get_arg(1).get_arg_name()))
                        case "bool":
                            temp_var.set_value(bool(self.get_arg(1).get_arg_name()))
                        case "string":
                            temp_var.set_value(str(self.get_arg(1).get_arg_name()))
                        case "nil":
                            temp_var.set_value(None)
                        
                    temp_var.set_type(self.get_arg(1).get_type())

                    match self.get_arg(0).get_frame():
                        case "GF":
                            check_var_declaration(self, program.global_frame, 0)
                            program.global_frame.vars[self.get_arg(0).get_arg_name()] = temp_var
                        case "LF":
                            check_var_declaration(self, program.local_frame, 0)
                            program.local_frame.vars[self.get_arg(0).get_arg_name()] = temp_var
                        case "TF":
                            check_var_declaration(self, program.temp_frame, 0)
                            program.temp_frame.vars[self.get_arg(0).get_arg_name()] = temp_var

                case "NOT":
                    pass
                case "INT2CHAR":
                    pass
                case "STRLEN":
                    pass
                case "TYPE":
                    pass
                case "CREATEFRAME":
                    pass
                case "PUSHFRAME":
                    pass
                case "POPFRAME":
                    pass
                case "RETURN":
                    pass
                case "BREAK":
                    pass
                case "DEFVAR":
                    match self.get_arg(0).get_frame():
                        case "GF":
                            program.global_frame.add_var(self.get_arg(0).get_arg_name())
                        case "LF":
                            program.local_frame = program.Frame(TypeFrame.LOCAL)
                            program.local_frame.add_var(self.get_arg(0).get_arg_name())
                            program.frame_stack.push(program.local_frame)
                        case "TF":
                            program.temp_frame = program.Frame(TypeFrame.TEMP)
                            program.temp_frame.add_var(self.get_arg(0).get_arg_name())
                case "POPS":
                    pass
                case "CALL":
                    pass
                case "LABEL":
                    pass
                case "JUMP":
                    pass
                case "PUSHS":
                    pass
                case "WRITE":
                    pass
                case "EXIT":
                    pass
                case "DPRINT":
                    pass
                case "ADD":
                    pass
                case "SUB":
                    pass
                case "MUL":
                    pass
                case "IDIV":
                    pass
                case "LT":
                    pass
                case "GT":
                    pass
                case "EQ":
                    pass
                case "AND":
                    pass
                case "OR":
                    pass
                case "STRI2INT":
                    pass
                case "CONCAT":
                    pass
                case "GETCHAR":
                    pass
                case "SETCHAR":
                    pass
                case "READ":
                    pass
                case "JUMPIFEQ":
                    pass
                case "JUMPIFNEQ":
                    pass
                case _:
                    print("ERROR: Unknown instruction", file=sys.stderr)
                    exit(32)

        # for debugging
        def __str__(self):
            return f"{self.opcode} {self.args}"

        class Argument:
            def __init__(self, type=None, value=None):
                self.type: str = type
                self.value = value

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

    class Frame:
        def __init__(self,type):
            self.vars = {}
            self.type: TypeFrame = type

        def add_var(self, var_name):
            self.vars[var_name] = self.Var()

        def print(self):
            for var in self.vars:
                print(var, self.vars[var])

        # for debugging
        def __str__(self):
            return f"{self.vars}"

        class Var:
            def __init__(self, type=None, value=None):
                self.type: str = type
                self.value = value

            def get_type(self):
                return self.type

            def set_type(self, type):
                self.type = type

            def get_frame(self):
                return super().type

            def get_value(self):
                return self.value

            def set_value(self, value):
                self.value = value

            # for debugging
            def __str__(self):
                return f"{self.type} {self.value}"

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

# maybe change this to gen_xml and create seperate check_xml func
def check_xml(xml_root):
    # check root element
    if xml_root.tag != "program":
        print("ERROR: Root element is not program", file=sys.stderr)
        exit(32)
    
    if "language" not in xml_root.attrib or xml_root.attrib["language"] != "IPPcode23":
        print("ERROR: Missing or invalid attribute", file=sys.stderr)
        exit(32)

    for instr in xml_root:
        check_instr(instr)

def check_instr(instr):
    if instr.tag != "instruction":
        print("ERROR: Element is not instruction", file=sys.stderr)
        exit(32)
    if "order" not in instr.attrib or re.match(r"^[0-9]+$", instr.attrib["order"]) is None:
        print("ERROR: Missing or invalid attribute (order)", file=sys.stderr)
        exit(32)

    if "opcode" not in instr.attrib:
        print("ERROR: Missing attribute (opcode)", file=sys.stderr)
        exit(32)

    match instr.attrib["opcode"]:
        case "MOVE"|"NOT"|"INT2CHAR"|"STRLEN"|"TYPE":
            check_var_symb(instr)
        case "CREATEFRAME"|"PUSHFRAME"|"POPFRAME"|"RETURN"|"BREAK":
            check_empty(instr)
        case "DEFVAR"|"POPS":
            check_var(instr)
        case "CALL"|"LABEL"|"JUMP":
            check_label(instr)
        case "PUSHS"|"WRITE"|"EXIT"|"DPRINT":
            check_symb(instr)
        case "ADD"|"SUB"|"MUL"|"IDIV"|"LT"|"GT"|"EQ"|"AND"|"OR"|"STRI2INT"|"CONCAT"|"GETCHAR"|"SETCHAR":
            check_var_2symb(instr)
        case "READ":
            check_var_type(instr)
        case "JUMPIFEQ"|"JUMPIFNEQ":
            check_label_2symb(instr)
        case _:
            print("ERROR: Invalid opcode", file=sys.stderr)
            exit(32)

def check_var_symb(instr):
    # check number of arguments
    if len(instr) != 2:
        print("ERROR: Invalid number of arguments", file=sys.stderr)
        exit(32)
    # check argument elements
    for arg in instr:
        if re.match(r"^(arg[12])$", arg.tag) is None: # not checking placements for each arg !!!
            print("ERROR: Element is not argument", file=sys.stderr)
            exit(32)
    # Check first argument (var)
    check_xml_attrib_type(instr[0], r"^(var)$")
    check_var_re(instr[0].text)
    # Check second argument (symb)
    symb_type = check_xml_attrib_type(instr[1], r"^(var|int|string|bool|nil)$")
    check_symb_re(instr[1].text, symb_type)

def check_var_2symb(instr):
    # check number of arguments
    if len(instr) != 3:
        print("ERROR: Invalid number of arguments", file=sys.stderr)
        exit(32)
    
    # check argument elements
    for arg in instr:
        if re.match(r"(^arg[123])$", arg.tag) is None:
            print("ERROR: Element is not argument", file=sys.stderr)
            exit(32)
        
    # Check first argument (var)
    check_xml_attrib_type(instr[0], r"^(var)$")
    check_var_re(instr[0].text)
    # Check second argument (symb)
    symb_type = check_xml_attrib_type(instr[1], r"^(var|int|string|bool|nil)$")
    check_symb_re(instr[1].text, symb_type)
    # Check third argument (symb)
    symb_type = check_xml_attrib_type(instr[2], r"^(var|int|string|bool|nil)$")
    check_symb_re(instr[2].text, symb_type)

def check_var_type(instr):
    # check number of arguments
    if len(instr) != 2:
        print("ERROR: Invalid number of arguments", file=sys.stderr)
        exit(32)

    # check argument elements
    for arg in instr:
        if re.match(r"^(arg[12])$", arg.tag) is None:
            print("ERROR: Element is not argument", file=sys.stderr)
            exit(32)
    
    # Check first argument (var)
    check_xml_attrib_type(instr[0], r"^(var)$")
    check_var_re(instr[0].text)
    # Check second argument (type)
    check_xml_attrib_type(instr[1], r"^(type)$")
    check_type_re(instr[1].text)

def check_label_2symb(instr):
    # check number of arguments
    if len(instr) != 3:
        print("ERROR: Invalid number of arguments", file=sys.stderr)
        exit(32)

    # check argument elements
    for arg in instr:
        if re.match(r"^(arg[123])$", arg.tag) is None:
            print("ERROR: Element is not argument", file=sys.stderr)
            exit(32)
    
    # Check first argument (label)
    check_xml_attrib_type(instr[0], r"^(label)$")
    check_label_re(instr[0].text)
    # Check second argument (symb)
    symb_type = check_xml_attrib_type(instr[1], r"^(var|int|string|bool|nil)$")
    check_symb_re(instr[1].text, symb_type)
    # Check third argument (symb)
    symb_type = check_xml_attrib_type(instr[2], r"^(var|int|string|bool|nil)$")
    check_symb_re(instr[2].text, symb_type)


def check_empty(instr):
    # check number of arguments
    if len(instr) != 0:
        print("ERROR: Invalid number of arguments", file=sys.stderr)
        exit(32)

def check_var(instr):
    # check number of arguments
    if len(instr) != 1:
        print("ERROR: Invalid number of arguments", file=sys.stderr)
        exit(32)

    # check argument elements
    if re.match(r"^(arg1)$", instr[0].tag) is None:
        print("ERROR: Element is not argument", file=sys.stderr)
        exit(32)
    # Check first argument (var)
    check_xml_attrib_type(instr[0], r"^(var)$")
    check_var_re(instr[0].text)

def check_label(instr):
    # check number of arguments
    if len(instr) != 1:
        print("ERROR: Invalid number of arguments", file=sys.stderr)
        exit(32)

    # check argument elements
    if re.match(r"^(arg1)$", instr[0].tag) is None:
        print("ERROR: Element is not argument", file=sys.stderr)
        exit(32)

    # Check first argument (label)
    check_xml_attrib_type(instr[0], r"^(label)$")
    check_label_re(instr[0].text)

def check_symb(instr):
    # check number of arguments
    if len(instr) != 1:
        print("ERROR: Invalid number of arguments", file=sys.stderr)
        exit(32)

    # check argument elements
    if re.match(r"^(arg1)$", instr[0].tag) is None:
        print("ERROR: Element is not argument", file=sys.stderr)
        exit(32)

    # Check first argument (symb)
    symb_type = check_xml_attrib_type(instr[0], r"^(var|int|string|bool|nil)$")
    check_symb_re(instr[0].text, symb_type)

def check_type(instr):
    # check number of arguments
    if len(instr) != 1:
        print("ERROR: Invalid number of arguments", file=sys.stderr)
        exit(32)

    # check argument elements
    if re.match(r"^arg1$", instr[0].tag) is None:
        print("ERROR: Element is not argument", file=sys.stderr)
        exit(32)

    # Check first argument (type)
    check_xml_attrib_type(instr[0], r"^(type)&")
    check_type_re(instr[0].text)

def check_var_re(var_value):
    if re.match(r"^(GF|LF|TF)@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$", var_value) is None:
        print("ERROR: Invalid variable value", file=sys.stderr)
        exit(32)

def check_symb_re(symb_value, symb_type):
    # if symb_value is None, we set it to empty string
    symb_value = "" if symb_value is None else symb_value
    match symb_type:
        case "var":
            if re.match(r"^(GF|LF|TF)@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$", symb_value) is None:
                print("ERROR: Invalid variable value", file=sys.stderr)
                exit(32)
        case "int":
            if re.match(r"^[+-]?(0x|0X)?[0-9]+$", symb_value) is None:
                print("ERROR: Invalid integer value", file=sys.stderr)
                exit(32)
        case "string":
            if re.match(r"^(\\[0-9]{3}|[^\\#\s])*$", symb_value) is None:
                print("ERROR: Invalid string value", file=sys.stderr)
                exit(32)
        case "bool":
            if re.match(r"^(true|false)$", symb_value) is None:
                print("ERROR: Invalid boolean value", file=sys.stderr)
                exit(32)
        case "nil":
            if re.match(r"^nil$", symb_value) is None:
                print("ERROR: Invalid nil value", file=sys.stderr)
                exit(32)

def check_label_re(label_value):
    if re.match(r"^([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$", label_value) is None:
        print("ERROR: Invalid label value", file=sys.stderr)
        exit(32)

def check_type_re(type_value):
    if re.match(r"^(int|string|bool)$", type_value) is None:
        print("ERROR: Invalid type value", file=sys.stderr)
        exit(32)

def check_xml_attrib_type(arg, regex):
    if "type" not in arg.attrib or re.match(regex, arg.attrib["type"]) is None:
        print("ERROR: Invalid or missing argument type", file=sys.stderr)
        exit(32) 
    return arg.attrib["type"]

def check_var_declaration(instruction, frame, arg_index):
    if instruction.get_arg(arg_index).get_arg_name() not in frame.vars:
        print("ERROR: Variable not declared", file=sys.stderr)
        exit(54)

def check_var_definition(instruction, frame, arg_index):
    if frame.vars[instruction.get_arg(arg_index).get_arg_name()].get_type() is None:
        print("ERROR: Variable not defined", file=sys.stderr)
        exit(56)

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

def check_order_attribute(program):
    # check duplicate order attributes
    dup_list = []
    for instr in program.instructions:
        if instr.order in dup_list:
            print("ERROR: Duplicate order attribute", file=sys.stderr)
            exit(32)
        dup_list.append(instr.order)


def sort_by_order(program):
    program.instructions.sort(key=lambda instr: int(instr.order))
    return program

def print_program():
    for instr in prg.instructions:
        print(instr.order+": ",instr.opcode)
        for arg in instr.args:
            print(arg.type, arg.value)

# Maybe just do it simply like this and do the rest in instruction class
def run_program(program):
    for instruction in program.instructions:
        instruction.run(program)

    program.print_frames()

if __name__ == "__main__":
    xml_root, input = parse_sc_args()
    check_xml(xml_root)
    gen_program(xml_root)
    prg = gen_program(xml_root)
    check_order_attribute(prg)
    prg = sort_by_order(prg)
    #print_program()
    run_program(prg)
    exit(0)