import sys
INSTRUCTIONS = []
BIT_INSTRUCTIONS = []
ERROR_LINES = []
VARIABLES = []
VAR_DICT = {}
LABEL_DICT = {}
OPCODE = {
    "add": "10000", "sub": "10001", "mul": "10110", "div": "10111", "xor": "11010", "or": "11011", "and": "11100",
    "mov": ["10010", "10011"], "rs": "11000", "ls": "11001",
    "not": "11101", "cmp": "11110",
    "ld": "10100", "st": "10101",
    "jmp": "11111", "jlt": "01100", "jgt": "01101", "je": "01111",
    "hlt": "01010"
}
REGISTER = {
    "R0": "000", "R1": "001", "R2": "010", "R3": "011", "R4": "100", "R5": "101", "R6": "110",
    "FLAGS": "111"
}

def getBinary(n):
    return bin(int(n)).replace("0b", "")

def getDecimal(n):
    return int(n, 2)

varCount = 0
instructionCount = 0

def labelCheck(instruction):
    if(len(instruction) == 1):
        if(instruction[0][-1] == ":"):
            ERROR_LINES.append("Error: Label Declared without Instruction:" + " ".join(instruction))
        else:
            ERROR_LINES.append("Error: Incomplete Instruction:" + " ".join(instruction))
    else:
        if(instruction[0][-1] != ":"):
            ERROR_LINES.append("Error: Wrong Declaration of Label:" + " ".join(instruction))
        if(instruction[1] == "var"):
            ERROR_LINES.append("Error: Variable Declared After Label:" + " ".join(instruction))
        if(instruction[0][:-1] in LABEL_DICT.keys()):
            ERROR_LINES.append("Error: Label Declared Already: " + " ".join(instruction))

def memoryAllocation(varCount, instructionCount):
    varStop = 0
    for instruction in INSTRUCTIONS:
        if(instruction[0] == "var"):
            if(varStop == 0):
                if(len(instruction) == 1):
                    ERROR_LINES.append("Error: Variable Declared without Value:" + " ".join(instruction))
                elif(instruction[1] in VARIABLES):
                    ERROR_LINES.append("Variable Declared Already: " + " ".join(instruction))
                else:
                    varCount += 1
                    VARIABLES.append(instruction[1])
            else:
                ERROR_LINES.append("Error: Variable Declared After Instruction:" + " ".join(instruction))
        elif(instruction[0] in OPCODE.keys()):
            varStop = 1
            instructionCount += 1
        else:
            varStop = 1
            labelCheck(instruction)
            if(instruction[0][-1] == ":"):
                LABEL_DICT[instruction[0][:-1]] = instructionCount
                instructionCount += 1
            instruction.remove(instruction[0])
    for variable in range(varCount):
        VAR_DICT[f"{VARIABLES[variable]}"] = instructionCount
        instructionCount += 1

def ISAtypeA(Opcode, Reg1, Reg2, Reg3):
    return (OPCODE[Opcode])+"00"+(REGISTER[Reg1])+REGISTER[Reg2]+(REGISTER[Reg3])

def ISAtypeB(OpCode, Register, num):
    if(OpCode == "mov"):
        opBits = OPCODE[OpCode][0]
    else:
        opBits = OPCODE[OpCode]
    bitVal = getBinary(num[1:])
    return opBits+REGISTER[Register]+("0"*(8-len(bitVal)))+bitVal

def ISAtypeC(OpCode, Register1, Register2):
    if(OpCode == "mov"):
        opBits = OPCODE[OpCode][1]
    else:
        opBits = OPCODE[OpCode]
    return opBits+"00000"+REGISTER[Register1]+REGISTER[Register2]

def ISAtypeD(OpCode, Register1, memAddress):
    var = getBinary(VAR_DICT[memAddress])
    return OPCODE[OpCode]+REGISTER[Register1]+("0"*(8-len(var)))+var

def ISAtypeE(OpCode, memAddress):
    varMemory = getBinary(LABEL_DICT[memAddress])
    return (OPCODE[OpCode])+"000"+("0"*(8-len(varMemory)))+getBinary(LABEL_DICT[memAddress])

def ISAtypeF(OpCode):
    return OPCODE[OpCode] + "00000000000"

def getType(OpCode):
    if(OpCode == "add" or OpCode == "sub" or OpCode == "mul" or OpCode == "xor" or OpCode == "or" or OpCode == "and"):
        return "A"
    elif(OpCode == "rs" or OpCode == "ls"):
        return "B"
    elif(OpCode == "div" or OpCode == "not" or OpCode == "cmp"):
        return "C"
    elif(OpCode == "st" or OpCode == "ld"):
        return "D"
    elif(OpCode == "jmp" or OpCode == "jlt" or OpCode == "jgt" or OpCode == "je"):
        return "E"
    elif(OpCode == "hlt"):
        return "F"
    else:
        return "Invalid"

def checkImmutable(assembly):
    if assembly[2][:1] != "$":
        ERROR_LINES.append("Error: Immutable Variable Not Used")
    else:
        try:
            number = int(assembly[2].strip("$"))
            if number >= 0 and number <= 255:
                return 1
            else:
                ERROR_LINES.append("Error: Immutable Variable Out Of Range: " +"( " + assembly[2].strip("$") + " is out of range" + " )")
        except:
            ERROR_LINES.append("Error: Invalid Number: " + " ".join(assembly))
    return 0

def flagCheck(assembly):
    if("FLAGS" in assembly):
        ERROR_LINES.append("Error: Invalid Use of Flag Register: "+" ".join(assembly))
        return 1
    return 0

def assemblyCheck():
    linecounter = 0
    hltcounter = 0
    for assembly in INSTRUCTIONS:
        linecounter += 1
        if(len(assembly) == 0):
            continue
        if(assembly[0] not in OPCODE.keys() and assembly[0] != "var" and assembly[0] not in LABEL_DICT.keys()):
            ERROR_LINES.append("Error: Invalid Instruction " +"In Line Number " + str(linecounter) + ": " + " ".join(assembly))
            continue
        if(assembly[0] in OPCODE.keys()):
            if(assembly[0] != "mov"):
                type = getType(assembly[0])
            else:
                try:
                    if(assembly[2] in REGISTER.keys()):
                        type = "C"
                    else:
                        type = "B"
                except:
                    ERROR_LINES.append("ERROR: Invalid Mov Instruction: "+" ".join(assembly))
                    continue
            if(type == "A" and len(assembly) == 4):
                if(assembly[1] not in REGISTER.keys() or assembly[2] not in REGISTER.keys() or assembly[3] not in REGISTER.keys()):
                    ERROR_LINES.append("Error: Invalid Register(s): " + " ".join(assembly))
                    continue
                if(flagCheck(assembly)):
                    continue
            elif(type == "B" and len(assembly) == 3):
                if (checkImmutable(assembly) == 0):
                    continue
                if(assembly[1] not in REGISTER.keys()):
                    ERROR_LINES.append("Error: Invalid Register Name: " + " ".join(assembly))
                    continue
                if(flagCheck(assembly)):
                    continue
            elif(type == "C" and len(assembly) == 3):
                if(assembly[1] not in REGISTER.keys() or assembly[2] not in REGISTER.keys()):
                    ERROR_LINES.append("Error: Invalid Register Used: " + " ".join(assembly))
                    continue
                if(assembly[0] != "mov"):
                    if(flagCheck(assembly)):
                        continue
                else:
                    if(assembly[2] == "FLAGS"):
                        ERROR_LINES.append("Error: Invalid Use of Flag Register: "+" ".join(assembly))
                        continue
            elif(type == "D" and len(assembly) == 3):
                if(assembly[2] in LABEL_DICT.keys()):
                    ERROR_LINES.append("Error: Invalid use of Label as Variable:"+" ".join(assembly))
                if(assembly[1] not in REGISTER.keys() or assembly[2] not in VAR_DICT.keys()):
                    ERROR_LINES.append("Error: Invalid Register/Variable Used: " + " ".join(assembly))
                    continue
                if(flagCheck(assembly)):
                    continue
            elif(type == "E" and len(assembly) == 2):
                if(assembly[1] in VAR_DICT.keys()):
                    ERROR_LINES.append("Error: Invalid use of Variable as Label: " + " ".join(assembly))
                if(assembly[1] not in LABEL_DICT.keys()):
                    ERROR_LINES.append("Error: Invalid Label Provided: " + " ".join(assembly))
                    continue
                if(flagCheck(assembly)):
                    continue
            elif(type == "F" and len(assembly) == 1):
                if(linecounter != len(INSTRUCTIONS)):
                    ERROR_LINES.append("Error: hlt Present Inbetween Instructions")
                    hltcounter += 1
                    continue
            else:
                ERROR_LINES.append("Error: Invalid Number of Arguments: " + " ".join(assembly))
                continue
    if(INSTRUCTIONS[len(INSTRUCTIONS)-1][0] != "hlt" and hltcounter == 0):
        ERROR_LINES.append("Error: hlt Instruction Missing")

def filereading():
    for instruction in sys.stdin:
        if(len(instruction.split()) == 0):
            continue
        else:
            INSTRUCTIONS.append(instruction.split())

def main():
    filereading()
    if(len(INSTRUCTIONS) > 256):
        ERROR_LINES.append("ERROR: Maximum Instructions Exceeded")
    if len(INSTRUCTIONS) == 0:
        print("Error: No Instructions")
        return
    memoryAllocation(varCount, instructionCount)
    assemblyCheck()
    if(len(ERROR_LINES) != 0):
        print("\n".join(ERROR_LINES))
        return
    for instruction in INSTRUCTIONS:
        if(instruction[0] != "mov"):
            type = getType(instruction[0])
        else:
            if(instruction[2] in REGISTER.keys()):
                type = "C"
            else:
                type = "B"
        if(type == "A"):
            BIT_INSTRUCTIONS.append(ISAtypeA(instruction[0], instruction[1], instruction[2], instruction[3]))
        elif(type == "B"):
            BIT_INSTRUCTIONS.append(ISAtypeB(instruction[0], instruction[1], instruction[2]))
        elif(type == "C"):
            BIT_INSTRUCTIONS.append(ISAtypeC(instruction[0], instruction[1], instruction[2]))
        elif(type == "D"):
            BIT_INSTRUCTIONS.append(ISAtypeD(instruction[0], instruction[1], instruction[2]))
        elif(type == "E"):
            BIT_INSTRUCTIONS.append(ISAtypeE(instruction[0], instruction[1]))
        elif(type == "F"):
            BIT_INSTRUCTIONS.append(ISAtypeF(instruction[0]))
    for bitInstruction in BIT_INSTRUCTIONS:
        print(bitInstruction)
    with open("output.txt", "w") as output:
        for bitInstruction in BIT_INSTRUCTIONS:
            output.write(bitInstruction + "\n")

main()
