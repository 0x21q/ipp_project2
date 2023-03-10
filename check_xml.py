import sys, re

# Checks if XML is valid
def check_xml(xml_root):
    # check root element
    if xml_root.tag != "program":
        print("ERROR: Root element is not program", file=sys.stderr)
        exit(32)
    
    if "language" not in xml_root.attrib or xml_root.attrib["language"] != "IPPcode23":
        print("ERROR: Missing or invalid attribute (language)", file=sys.stderr)
        exit(32)

    for instr in xml_root:
        check_instr(instr)

# Checks if XML instruction is valid
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

    match instr.attrib["opcode"].upper():
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

# Checks if XML arguments (var, symb) are valid
def check_var_symb(instr):
    check_xml_arguments(instr, 2)
    # Check first argument (var)
    check_xml_attrib_type(instr[0], r"^(var)$")
    check_var_re(instr[0].text)
    # Check second argument (symb)
    symb_type = check_xml_attrib_type(instr[1], r"^(var|int|string|bool|nil)$")
    check_symb_re(instr[1].text, symb_type)

# Checks if XML arguments (var, symb, symb) are valid
def check_var_2symb(instr):
    check_xml_arguments(instr, 3) 
    # Check first argument (var)
    check_xml_attrib_type(instr[0], r"^(var)$")
    check_var_re(instr[0].text)
    # Check second argument (symb)
    symb_type = check_xml_attrib_type(instr[1], r"^(var|int|string|bool|nil)$")
    check_symb_re(instr[1].text, symb_type)
    # Check third argument (symb)
    symb_type = check_xml_attrib_type(instr[2], r"^(var|int|string|bool|nil)$")
    check_symb_re(instr[2].text, symb_type)

# Checks if XML arguments (var, type) are valid
def check_var_type(instr):
    check_xml_arguments(instr, 2) 
    # Check first argument (var)
    check_xml_attrib_type(instr[0], r"^(var)$")
    check_var_re(instr[0].text)
    # Check second argument (type)
    check_xml_attrib_type(instr[1], r"^(type)$")
    check_type_re(instr[1].text)

# Checks if XML arguments (label, symb, symb) are valid
def check_label_2symb(instr):
    check_xml_arguments(instr, 3) 
    # Check first argument (label)
    check_xml_attrib_type(instr[0], r"^(label)$")
    check_label_re(instr[0].text)
    # Check second argument (symb)
    symb_type = check_xml_attrib_type(instr[1], r"^(var|int|string|bool|nil)$")
    check_symb_re(instr[1].text, symb_type)
    # Check third argument (symb)
    symb_type = check_xml_attrib_type(instr[2], r"^(var|int|string|bool|nil)$")
    check_symb_re(instr[2].text, symb_type)

# Checks if XML without arguments is valid
def check_empty(instr):
    # check number of arguments
    if len(instr) != 0:
        print("ERROR: Invalid number of arguments", file=sys.stderr)
        exit(32)

# Checks if XML argument (var) is valid
def check_var(instr):
    check_xml_arguments(instr, 1)
    # Check first argument (var)
    check_xml_attrib_type(instr[0], r"^(var)$")
    check_var_re(instr[0].text)

# Checks if XML argument (label) is valid
def check_label(instr):
    check_xml_arguments(instr, 1)
    # Check first argument (label)
    check_xml_attrib_type(instr[0], r"^(label)$")
    check_label_re(instr[0].text)

# Checks if XML argument (symb) is valid
def check_symb(instr):
    check_xml_arguments(instr, 1)
    # Check first argument (symb)
    symb_type = check_xml_attrib_type(instr[0], r"^(var|int|string|bool|nil)$")
    check_symb_re(instr[0].text, symb_type)

# Checks if XML argument (type) is valid
def check_type(instr):
    check_xml_arguments(instr, 1)
    # Check first argument (type)
    check_xml_attrib_type(instr[0], r"^(type)&")
    check_type_re(instr[0].text)

# Checks var name with regex
def check_var_re(var_value):
    if re.match(r"^(GF|LF|TF)@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$", var_value) is None:
        print("ERROR: Invalid variable value", file=sys.stderr)
        exit(32)

# Checks symb name with regex
def check_symb_re(symb_value, symb_type):
    # if symb_value is None, we set it to empty string
    symb_value = "" if symb_value is None else symb_value
    match symb_type:
        case "var":
            if re.match(r"^(GF|LF|TF)@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$", symb_value) is None:
                print("ERROR: Invalid variable value", file=sys.stderr)
                exit(32)
        case "int":
            valid_int = False
            if re.match(r"^[+-]?(0x|0X)[\da-fA-F]+(_[\da-fA-F]+)*$", symb_value) is None:
                valid_int = True
            elif 'o' in symb_value or 'O' in symb_value:
                if re.match(r"^[+-]?0(o|O)?[0-7]+(_[0-7]+)*$", symb_value) is None:
                    valid_int = True
            elif re.match(r"^[+-]?0+[0-7]*(_[0-7]+)*$", symb_value) is None:
                valid_int = True
            elif re.match(r"^[+-]?[1-9][\d]*(_[\d]+)*$", symb_value) is None:
                valid_int = True
            if not valid_int:
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

# Checks label name with regex
def check_label_re(label_value):
    if re.match(r"^([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$", label_value) is None:
        print("ERROR: Invalid label value", file=sys.stderr)
        exit(32)

# Checks type name with regex
def check_type_re(type_value):
    if re.match(r"^(int|string|bool)$", type_value) is None:
        print("ERROR: Invalid type value", file=sys.stderr)
        exit(32)

# Checks if XML attribute (type) is valid
def check_xml_attrib_type(arg, regex):
    if "type" not in arg.attrib or re.match(regex, arg.attrib["type"]) is None:
        print("ERROR: Invalid or missing argument type", file=sys.stderr)
        exit(32) 
    return arg.attrib["type"]

# Checks if XML arguments are valid
def check_xml_arguments(instr, number_of_args):
    # check number of arguments
    if len(instr) != number_of_args:
        print("ERROR: Invalid number of arguments", file=sys.stderr)
        exit(32)

    # check argument elements, doesn't check duplicate arguments
    if number_of_args == 1:
        if instr.find("arg1") is None:
            print("ERROR: Instruction is missing an argument", file=sys.stderr)
            exit(32)
    elif number_of_args == 2:
        if instr.find("arg1") is None or instr.find("arg2") is None:
            print("ERROR: Instruction is missing an argument", file=sys.stderr)
            exit(32)
    else:
        if instr.find("arg1") is None or instr.find("arg2") is None or instr.find("arg3") is None:
            print("ERROR: Instruction is missing an argument", file=sys.stderr)
            exit(32)