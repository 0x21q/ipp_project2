#!/usr/bin/python3.10
import argparse, re, os.path, sys
import xml.etree.ElementTree as ET
from enum import Enum

class Program:
    def  __init__(self):
        self.instructions = []
        self.data_stack = []
        self.frame_stack = []
        self.global_frame = self.Frame(TypeFrame.GLOBAL) 
        self.local_frame = None
        self.temp_frame = None

    def add_instr(self, instr):
        self.instructions.append(instr)

    def add_data(self, data):
        self.data_stack.append(data)

    def add_local_frame(self, frame):
        self.frame_stack.append(frame)

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

        def run(self):
            pass

        # for debugging
        def __str__(self):
            return f"{self.opcode} {self.args}"

        class Argument:
            def __init__(self, type=None, value=None):
                self.type: str = type
                self.value = value

            # for debugging
            def __str__(self):
                return f"{self.type} {self.value}"

    class Frame:
        def __init__(self,type):
            self.vars = {}
            self.type = type

        def add_var(self, var):
            self.vars[var] = None

        # for debugging
        def __str__(self):
            return f"{self.vars}"

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

def gen_program(xml_root):
    program = Program()
    for instr in xml_root:
        instr_obj = Program.Instruction(instr.attrib["opcode"], instr.attrib["order"])
        for arg in instr:
            arg_obj = Program.Instruction.Argument(arg.attrib["type"], arg.text)
            instr_obj.add_arg(arg_obj)
        program.add_instr(instr_obj)
    return program

def sort_by_order(program):
    program.instructions.sort(key=lambda instr: int(instr.order))
    return program

def print_program():
    for instr in prg.instructions:
        print(instr.order+": ",instr.opcode)
        for arg in instr.args:
            print(arg.type, arg.value)

def run_program(program):
    pass


if __name__ == "__main__":
    xml_root, input = parse_sc_args()
    check_xml(xml_root)
    gen_program(xml_root)
    prg = gen_program(xml_root)
    prg = sort_by_order(prg)
    print_program()
    run_program(prg)
    exit(0)