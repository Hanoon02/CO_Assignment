import sys
import struct
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
    "hlt": "01010",
    "addf": "00000", "subf": "00001",
    "movf": "00010"  # move float
}
REGISTER = {
    "R0": "000", "R1": "001", "R2": "010", "R3": "011", "R4": "100", "R5": "101", "R6": "110",
    "FLAGS": "111"
}


def getBinary(n):
    return bin(int(n)).replace("0b", "")


def getDecimal(n):
    return int(n, 2)


def getFloat(num):
    bits, = struct.unpack('!I', struct.pack('!f', float(num)))
    IEEENotation = "{:032b}".format(bits)
    exponent = IEEENotation[1:9]
    mantissa = IEEENotation[9:]
    actualExponent = getDecimal(exponent) - 127
    binExponent = getBinary(actualExponent)
    extraBits = "0"*(3-len(binExponent))
    return (extraBits+binExponent+mantissa[:5])

varCount = 0
instructionCount = 0


def labelCheck(instruction, lineCount):
    if(len(instruction) == 1):
        if(instruction[0][-1] == ":"):
            ERROR_LINES.append("Error: Label Declared without Instruction:" +"In Line Number " + str(lineCount) + ": " + " ".join(instruction))
        else:
            ERROR_LINES.append("Error: Incomplete Instruction:" +"In Line Number " + str(lineCount) + ": " + " ".join(instruction))
    else:
        if(instruction[0][-1] != ":"):
            ERROR_LINES.append("Error: Wrong Declaration of Label:" +"In Line Number " + str(lineCount) + ": " + " ".join(instruction))
        if(instruction[1] == "var"):
            ERROR_LINES.append("Error: Variable Declared After Label:" +"In Line Number " + str(lineCount) + ": " + " ".join(instruction))
        if(instruction[0][:-1] in LABEL_DICT.keys()):
            ERROR_LINES.append("Error: Label Declared Already: " +"In Line Number " + str(lineCount) + ": " + " ".join(instruction))


def memoryAllocation(varCount, instructionCount):
    varStop = 0
    lineCount = 0
    for instruction in INSTRUCTIONS:
        lineCount += 1
        if(instruction[0] == "var"):
            if(varStop == 0):
                if(len(instruction) == 1):
                    ERROR_LINES.append("Error: Variable Declared without Value:" +"In Line Number " + str(lineCount) + ": " + " ".join(instruction))
                elif(instruction[1] in VARIABLES):
                    ERROR_LINES.append("Variable Declared Already: " + "In Line Number " + str(lineCount) + ": " + " ".join(instruction))
                else:
                    varCount += 1
                    VARIABLES.append(instruction[1])
            else:
                ERROR_LINES.append("Error: Variable Declared After Instruction:" +"In Line Number " + str(lineCount) + ": " + " ".join(instruction))
        elif(instruction[0] in OPCODE.keys()):
            varStop = 1
            instructionCount += 1
        else:
            varStop = 1
            labelCheck(instruction, lineCount)
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

    if (OpCode == "movf"):
        opBits = OPCODE[OpCode]
        return (opBits + REGISTER[Register] + getFloat(float(num[1:])))

    elif (OpCode == "mov"):
        bitVal = getBinary(num[1:])
        opBits = OPCODE[OpCode][0]
        return (opBits+REGISTER[Register]+("0"*(8-len(bitVal)))+bitVal)

    else:
        bitVal = getBinary(num[1:])
        opBits = OPCODE[OpCode]
        return (opBits+REGISTER[Register]+("0"*(8-len(bitVal)))+bitVal)


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
    if(OpCode == "add" or OpCode == "sub" or OpCode == "mul" or OpCode == "xor" or OpCode == "or" or OpCode == "and" or OpCode == "addf" or OpCode == "subf"):
        return "A"
    elif(OpCode == "rs" or OpCode == "ls" or OpCode == "movf"):
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


def checkImmutable_or_floatImmutable(assembly, linecounter):
    if assembly[2][:1] != "$":
        ERROR_LINES.append("Error: Immutable Variable Not Used" +"In Line Number " + str(linecounter))
    else:
        try:
            number = eval(assembly[2].strip("$"))
            typenum = type(number)
            if (typenum is int and assembly[0] == "mov"):
                if (number >=0 and number<=255):
                    return 1
                else:
                    ERROR_LINES.append("Error: Immutable Variable Out Of Range: " + "( " + number + " is out of range" + " )" + " In Line Number " + str(linecounter))
            elif (typenum is int and assembly[0] == "movf"):
                ERROR_LINES.append("Error: Invalid Float Number: " + " In Line Number " +str(linecounter) + ": " + " ".join(assembly))
            elif (typenum is float and assembly[0] == "movf"):
                return 1
            elif (typenum is float and assembly[0] == "mov"):
                ERROR_LINES.append("Error: Invalid Number: " + " In Line Number " +str(linecounter) + ": " + " ".join(assembly))
        except:
            ERROR_LINES.append("Error: Invalid Number: " + "In Line Number " +str(linecounter) + ": " + " ".join(assembly))
    return 0


def flagCheck(assembly, linecounter):
    if("FLAGS" in assembly):
        ERROR_LINES.append("Error: Invalid Use of Flag Register: " +"In Line Number " + str(linecounter) + ": " + " ".join(assembly))
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
                    ERROR_LINES.append("ERROR: Invalid Mov Instruction" +"In Line Number " + str(linecounter) + ": " + " ".join(assembly))
                    continue
            if(type == "A" and len(assembly) == 4):
                if(assembly[1] not in REGISTER.keys() or assembly[2] not in REGISTER.keys() or assembly[3] not in REGISTER.keys()):
                    ERROR_LINES.append("Error: Invalid Register(s) " + "In Line Number " + str(linecounter) + ": " + " ".join(assembly))
                    continue
                if(flagCheck(assembly, linecounter)):
                    continue
            elif(type == "B" and len(assembly) == 3):
                if (checkImmutable_or_floatImmutable(assembly, linecounter) == 0):
                    continue
                if(assembly[1] not in REGISTER.keys()):
                    ERROR_LINES.append("Error: Invalid Register Name " +"In Line Number " + str(linecounter) + ": " + " ".join(assembly))
                    continue
                if(flagCheck(assembly, linecounter)):
                    continue
            elif(type == "C" and len(assembly) == 3):
                if(assembly[1] not in REGISTER.keys() or assembly[2] not in REGISTER.keys()):
                    ERROR_LINES.append("Error: Invalid Register Used " +"In Line Number " + str(linecounter) + ": " + " ".join(assembly))
                    continue
                if(assembly[0] != "mov"):
                    if(flagCheck(assembly, linecounter)):
                        continue
                else:
                    if(assembly[2] == "FLAGS"):
                        ERROR_LINES.append("Error: Invalid Use of Flag Register " +"In Line Number " + str(linecounter) + ": " + " ".join(assembly))
                        continue
            elif(type == "D" and len(assembly) == 3):
                if(assembly[2] in LABEL_DICT.keys()):
                    ERROR_LINES.append("Error: Invalid use of Label as Variable:" +"In Line Number " + str(linecounter) + ": " + " ".join(assembly))
                if(assembly[1] not in REGISTER.keys() or assembly[2] not in VAR_DICT.keys()):
                    ERROR_LINES.append("Error: Invalid Register/Variable Used " +"In Line Number " + str(linecounter) + ": " + " ".join(assembly))
                    continue
                if(flagCheck(assembly, linecounter)):
                    continue
            elif(type == "E" and len(assembly) == 2):
                if(assembly[1] in VAR_DICT.keys()):
                    ERROR_LINES.append("Error: Invalid use of Variable as Label: " +"In Line Number " + str(linecounter) + ": " + " ".join(assembly))
                if(assembly[1] not in LABEL_DICT.keys()):
                    ERROR_LINES.append("Error: Invalid Label Provided " +"In Line Number " + str(linecounter) + ": " + " ".join(assembly))
                    continue
                if(flagCheck(assembly, linecounter)):
                    continue
            elif(type == "F" and len(assembly) == 1):
                if(linecounter != len(INSTRUCTIONS)):
                    ERROR_LINES.append("Error: hlt Present Inbetween Instructions" + "In Line Number " + str(linecounter))
                    hltcounter += 1
                    continue
            else:
                ERROR_LINES.append("Error: Invalid Number of Arguments: " + "In Line Number " + str(linecounter) + ": " + " ".join(assembly))
                continue
    if(len(INSTRUCTIONS[len(INSTRUCTIONS)-1]) != 0):
        if(INSTRUCTIONS[len(INSTRUCTIONS)-1][0] != "hlt" and hltcounter == 0):
            ERROR_LINES.append("Error: hlt Instruction Missing")


def filereading():
    for instruction in sys.stdin:
        if(len(instruction.split()) == 0):
            continue
        else:
            INSTRUCTIONS.append(instruction.split())
    with open("input.txt", "w") as file:
        for instruction in INSTRUCTIONS:
            file.write(" ".join(instruction) + "\n")


def execute():
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


def main():
    filereading()
    if len(INSTRUCTIONS) == 0:
        print("Error: No Instructions")
        return
    memoryAllocation(varCount, instructionCount)
    assemblyCheck()
    if(len(ERROR_LINES) != 0):
        print("\n".join(ERROR_LINES))
        with open("output.txt", "w") as output:
            for error in ERROR_LINES:
                output.write(error + "\n")
        return
    execute()
    if(len(BIT_INSTRUCTIONS) > 256):
        print("ERROR: Maximum Instructions Exceeded")
        return
    for bitInstruction in BIT_INSTRUCTIONS:
        print(bitInstruction)
    with open("output.txt", "w") as output:
        for bitInstruction in BIT_INSTRUCTIONS:
            output.write(bitInstruction + "\n")


main()
