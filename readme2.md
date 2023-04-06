# Implementation documentation for Task 2 of the IPP 2022/2023

Name and surname: Jakub Kratochvíl

Login: xkrato67

## Project structure:
The project is structured in two files. The first is `interpret.py`, as given by the assignment
which contains the most of the program functionality inluding class definitions.
The second file is `check_xml.py` which includes functions for checking a xml structure given on 
the input.

## Class diagram
Information about classes + diagram.

## Solution method
### Processing command line arguments
Parsing of argument using argparse.

### Checking XML strucutre
Information about how check_xml works and what each functions does

### Implementation of OOP
As seen in the class diagram above, most of the classes have associtation which is composition.
I found it convenient to display the composition as the nesting within the classes.
When objects are in composition, it means that the child class doesn't exists if the parent class 
doesn't exists, which nesting implies aswell. For example when we want to call the the constructor
for the Instruction class, it has to be called as `Program.Instruction()` which shows that Program 
object has to exist in order to use the Instruction constructor.

### Running the program
When program is being run, firstly commandline arguments are checked with function called 
`parse_sc_args()`. If the arguments are loaded correctly the program checks the structure of the 
xml provided either in the file or stdin using `check_xml()`. Next step is iterating over the 
checked xml tree and generating instructions and labels with `gen_program()`. After the program 
objects are generated, program checks the instruction order with `check_order_attribute()` and 
sorts the instructions by this order with `sort_by_order()` and then executes the program with 
`prg.run()`. If the execution ended successfully program returns zero, otherwise it returns 
corresponding error code.
