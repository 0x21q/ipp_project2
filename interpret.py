#!/usr/bin/python3.10
import argparse, re, os.path, sys
import xml.etree.ElementTree as ET

class Program:
    def  __init__(self):
        self.instructions = []

    def add_instr(self, instr):
        self.instructions.append(instr)
    
    # for debugging
    def __str__(self):
        return f"{self.opcode} {self.args}"

    class Instruction:
        def __init__(self):
            self.opcode = ""
            self.args = []
            self.arg_count = 0
        
        def set_opcode(self, opcode):
            self.opcode = opcode
            
        def add_args(self, arg1=None, arg2=None, arg3=None):
            if arg1 is not None:
                self.args.append(arg1)
                self.arg_count += 1
            if arg2 is not None:
                self.args.append(arg2)
                self.arg_count += 1
            if arg3 is not None:
                self.args.append(arg3)
                self.arg_count += 1

        # for debugging
        def __str__(self):
            return f"{self.opcode} {self.args}"

        class Argument:
            def __init__(self):
                self.type = ""
                self.value = None

            def set_type(self, type):
                self.type = type

            def set_value(self, value):
                self.value = value
            
            # for debugging
            def __str__(self):
                return f"{self.type} {self.value}"


# Parsing script arguments
def parse_sc_args():
    sc_args = argparse.ArgumentParser(description="Interprets code in XML format")
    sc_args.add_argument("-s","--source", type=str)
    sc_args.add_argument("-i","--input", type=str)
    return sc_args.parse_args()

def main():
    if sc_args_parsed.source is None and sc_args_parsed.input is None:
        print("ERROR: No source file or input file specified", file=sys.stderr)
        exit(10)
    elif sc_args_parsed.source is None:
        # load source from stdin
        source = sys.stdin.read()
    elif sc_args_parsed.input is None:
        # load input from stdin
        input = sys.stdin.read()


if __name__ == "__main__":
    sc_args_parsed = parse_sc_args()
    main()