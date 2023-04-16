# Implementation documentation for Task 2 of the IPP 2022/2023

Name and surname: Jakub Kratochvíl

Login: xkrato67

## Project structure:
The project is structured in two files. The first is `interpret.py`, as given by the assignment
which contains the most of the program functionality inluding class definitions.
The second file is `check_xml.py` which includes functions for checking a xml structure given on 
the input.

## Class diagram
The classes in the implementation have only instance attributes, in the diagram they are 
displayed as class attributes to make diagram more clear.

![class-diagram](doc-img/class_diagram.png)

The classes used in the project are `Program`, `Instruction`, `Argument`, `Frame`, `Var` and
`Stack`. The main class of the whole project is `Program` which holds all data of the interpreted 
program. When instanciated, it creates empty list of intructions, necessary stacks, frames and
initialize a program counter. More information can be seen in the diagram above.
I would like to point out the execution of the individual instruction which is done using 
inheritance. The method of the instruction class called `Instruction` calls the `execute()` 
method which selects and calls the method of the respective child class using dictionary
mapping and executes the instruction.

### Example of dictionary mapping from the implementation
```python
def execute(self, program):
            # Maps opcode to specific instruction child class
            opcode_to_class = {
                "MOVE": program.Move,
                 ...
                "JUMPIFNEQ": program.Jumpifneq
            }
            # Calls execute method of specific instruction child class
            opcode_to_class[self.get_opcode()].execute(self,program)
```

### Class nesting
As seen in the class diagram above, most of the classes have associtation which is composition.
I found it convenient to display the composition as the nesting within the classes.
When objects are in composition, it means that the child class doesn't exists if the parent class 
doesn't exists, which nesting implies aswell. For example when we want to call the the constructor
for the Instruction class, it has to be called as `Program.Instruction()` which shows that Program 
object has to exist in order to use the Instruction constructor.

## Program execution order
When program is being run, firstly command line arguments are checked using library called 
argparse in the function called `parse_sc_args()`, which handles all cases of loading arguments
given by the assignment including errors of loading XML structure into XMLtree.
After the XMLtree is successfully loaded whole tree is being scanned with the function called 
`check_xml()` which loops though every XML structure and does all necessary XML checks,
syntax checks and also sorting of arguments. Since in the 
assignment was stated that we cannot trust user input I found it appropriate to do
similiar syntax checks as in the parser.
Next step is iterating over the checked XMLtree and generating instructions and labels with
`gen_program()`. After the program objects are generated, program checks the instruction order
with `check_order_attribute()` and sorts the instructions by this order with `sort_by_order()`
and then executes the program with `prg.run()`. If the execution ended successfully program 
returns zero, otherwise it returns corresponding error code.
