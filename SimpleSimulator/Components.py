from matplotlib import pyplot
import sys
import struct
from collections import OrderedDict
def getBinary(n):
    return bin(int(n)).replace("0b", "")
def getDecimal(n):
    return int(n, 2)
def getFloat(n):
    exponentsValue = getDecimal(n[0:3])
    mantissaWholePart = n[3:exponentsValue+3]
    mantissaFractionalPart = n[exponentsValue+3:]
    fractionalValue=0
    for i in range(len(mantissaFractionalPart)):
        fractionalValue += int(mantissaFractionalPart[i])*(2**(-i-1))
    wholeValue = getDecimal("1"+mantissaWholePart)
    return wholeValue+fractionalValue
def getIEEEFloat(num):
    bits, = struct.unpack('!I', struct.pack('!f', float(num)))
    IEEENotation = "{:032b}".format(bits)
    exponent = IEEENotation[1:9]
    mantissa = IEEENotation[9:]
    actualExponent = getDecimal(exponent) - 127
    binExponent = getBinary(actualExponent)
    extraBits = "0"*(3-len(binExponent))
    return (extraBits+binExponent+mantissa[:5])
class ProgramCounter:
    PCValue = 0
    cycleCounter = 0
    jumpSet = -1
    def dump(self):
        if(self.jumpSet==-1):
            binarynum = getBinary(self.PCValue-1)
            emptyBits = "0"*(8-len(binarynum))
            binnum = emptyBits+binarynum
            #print(f"{self.PCValue}:", end=" ")
            print(binnum, end=" ")
        else:
            binarynum = getBinary(self.jumpSet)
            emptyBits = "0"*(8-len(binarynum))
            binnum = emptyBits+binarynum
            #print(f"{self.PCValue}:", end=" ")
            print(binnum, end=" ") 
    def update(self, nextPC):
        ProgramCounter.PCValue = nextPC
    def getValue(self):
        return self.PCValue
class RegisterFile:
    allRegisterValues = {"000": 0, "001": 0, "010": 0,"011": 0, "100": 0, "101": 0, "110": 0, "111": 0}
    allVariables={}
    def dump(self):
        for register in self.allRegisterValues:
            if(isinstance(self.allRegisterValues[register], int)):
                regBits = getBinary(self.allRegisterValues[register])
                emptyBits = "0"*(16-len(regBits))
                #print(self.allRegisterValues[register], end=" ")
                if register!="111":
                    print(emptyBits+regBits, end=" ")
                else:
                    print(emptyBits+regBits)
            else:
                regBits = getIEEEFloat(self.allRegisterValues[register])
                emptyBits = "0"*(16-len(regBits))
                #print(self.allRegisterValues[register], end=" ")
                if register!="111":
                    print(emptyBits+regBits, end=" ")
                else:
                    print(emptyBits+regBits)

    def getRegister(self, register, floatCheck):
        if(floatCheck==1):
            if(isinstance(self.allRegisterValues[register], int)):
                bitConvertion = getBinary(self.allRegisterValues[register])
                if(len(bitConvertion)<8):
                    extraBits = (8-len(bitConvertion))*"0"
                    finalBitNum = extraBits+bitConvertion
                    return getFloat(finalBitNum)
                else:
                    return getFloat(bitConvertion[-8:])
            else:
                return self.allRegisterValues[register]
        else:
            if(isinstance(self.allRegisterValues[register], float)):
                bitConvertion = getIEEEFloat(self.allRegisterValues[register])
                decimalConvertion = getDecimal(bitConvertion)
                return decimalConvertion
            else:
                return self.allRegisterValues[register]
    def updateRegister(self, newValue, register):
        self.allRegisterValues[register] = newValue
    
    def getVariable(self, variable):
        if(variable in self.allVariables.keys()):
            return self.allVariables[variable]
        else:
            return 0
    
    def updateVariable(self, variable, value):
        self.allVariables[variable] = value
    
    def flagReset(self):
        self.allRegisterValues["111"] = 0
class ExecutionEngine:
    isHalt = False
    def getType(self, OpCode):
        if(OpCode == "10000" or OpCode == "10001" or OpCode == "10110" or OpCode == "11011" or OpCode == "11010" or OpCode == "11100" or OpCode =="00000" or OpCode=="00001"):
            return "A"
        elif(OpCode == "11000" or OpCode == "11001" or OpCode =="00010"):
            return "B"
        elif(OpCode == "10111" or OpCode == "11101" or OpCode == "11110"):
            return "C"
        elif(OpCode == "10101" or OpCode == "10100"):
            return "D"
        elif(OpCode == "11111" or OpCode == "01100" or OpCode == "01101" or OpCode == "01111"):
            return "E"
        elif(OpCode == "01010"):
            return "F"
    def ISATypeA(self, instruction):
        if(instruction[0:5] == "10000"):  # for addition
            newValue = RegisterFile().getRegister(instruction[7:10],0) + RegisterFile().getRegister(instruction[10:13],0)
            if newValue<(2**16):
                RegisterFile().updateRegister(newValue, instruction[13:16])
                RegisterFile().flagReset()
            else:
                RegisterFile().updateRegister(8, "111")
                RegisterFile().updateRegister(newValue%(2**16), instruction[13:16])
        elif (instruction[0:5] == "00000"):  # for addition in fraction
            newValue = RegisterFile().getRegister(instruction[7:10],1) + RegisterFile().getRegister(instruction[10:13],1)
            if newValue<(2**16):
                RegisterFile().updateRegister(newValue, instruction[13:16])
            else:
                RegisterFile().updateRegister(8, "111")
                RegisterFile().updateRegister(255, instruction[13:16])
        elif(instruction[0:5] == "10001"):  # for subtraction
            newValue = RegisterFile().getRegister(instruction[7:10],0) - RegisterFile().getRegister(instruction[10:13],0)
            if newValue>=0:
                RegisterFile().updateRegister(newValue, instruction[13:16])
                RegisterFile().flagReset()
            else:
                RegisterFile().updateRegister(8, "111")
                RegisterFile().updateRegister(0, instruction[13:16])
        elif(instruction[0:5] == "00001"):  # for subtraction in fraction
            newValue = RegisterFile().getRegister(instruction[7:10],1) - RegisterFile().getRegister(instruction[10:13],1)
            if newValue>1:
                RegisterFile().updateRegister(newValue, instruction[13:16])
            else:
                RegisterFile().updateRegister(8, "111")
                RegisterFile().updateRegister(0, instruction[13:16])  
        elif(instruction[0:5] == "10110"):  # for multiply
            newValue = RegisterFile().getRegister(instruction[7:10],0) * RegisterFile().getRegister(instruction[10:13],0)
            if newValue<(2**16):
                RegisterFile().updateRegister(newValue, instruction[13:16])
                RegisterFile().flagReset()
            else:
                RegisterFile().updateRegister(8, "111")
                RegisterFile().updateRegister(newValue%(2**16), instruction[13:16])
        elif(instruction[0:5] == "11010"):
            newValue = RegisterFile().getRegister(instruction[7: 10],0) ^ RegisterFile().getRegister(instruction[10: 13],0)
            RegisterFile().updateRegister(newValue, instruction[13:16])
            RegisterFile().flagReset()
        elif(instruction[0:5] == "11011"):  # for OR
            newValue = RegisterFile().getRegister(instruction[7: 10],0) | RegisterFile().getRegister(instruction[10: 13],0)
            RegisterFile().updateRegister(newValue, instruction[13:16])
            RegisterFile().flagReset()
        elif(instruction[0:5] == "11100"):  # for AND
            newValue = RegisterFile().getRegister(instruction[7: 10],0) & RegisterFile().getRegister(instruction[10: 13],0)
            RegisterFile().updateRegister(newValue, instruction[13:16])
            RegisterFile().flagReset()
    def ISATypeB(self, instruction):
        if(instruction[0:5] == "11000"):  # for right shift
            newValue = RegisterFile().getRegister(instruction[7: 10],0) >> RegisterFile().getRegister(instruction[10: 13],0)
            RegisterFile().updateRegister(newValue, instruction[13:16])
            RegisterFile().flagReset()
        elif(instruction[0:5] == "11001"):  # for left shift
            newValue = RegisterFile().getRegister(instruction[7: 10],0) << RegisterFile().getRegister(instruction[10: 13],0)
            RegisterFile().updateRegister(newValue, instruction[13:16])
            RegisterFile().flagReset()
        elif(instruction[0:5] == "10010"):  # for mov IMM
## TO DO
            newValue = getDecimal(instruction[8:16])
            RegisterFile().updateRegister(newValue, instruction[5:8])
            RegisterFile().flagReset()
## TO DO
        elif(instruction[0:5] == "00010"):
            newValue = getFloat(instruction[8:16])
            RegisterFile().updateRegister(newValue, instruction[5:8])
            RegisterFile().flagReset()
    def ISATypeC(self, instruction):
        if(instruction[0:5] == "10011"):  # for mov
            newValue = RegisterFile().getRegister(instruction[10:13],0)
            RegisterFile().updateRegister(newValue,instruction[13:16])
            RegisterFile().flagReset()
        elif(instruction[0:5] == "10111"):  # for divide
            newValue1 = RegisterFile().getRegister(instruction[10:13],0) // RegisterFile().getRegister(instruction[13:16],0)
            RegisterFile().updateRegister(newValue1, "000")
            newValue2 = RegisterFile().getRegister(instruction[10:13],0) % RegisterFile().getRegister(instruction[13:16],0)
            RegisterFile().updateRegister(newValue2, "001")
            RegisterFile().flagReset()
        elif(instruction[0:5] == "11101"):  # for not
            newValue= 65535 - RegisterFile().getRegister(instruction[10:13],0)
            binNewValue = getBinary(newValue)
            if(len(binNewValue)<16):
                binNewValue = "0"*(16-len(binNewValue)) + binNewValue
                newDecimalValue = getDecimal(binNewValue)
                RegisterFile().updateRegister(newDecimalValue, instruction[13:16])
            else:
                newDecimalValue = getDecimal(binNewValue)
                RegisterFile().updateRegister(newDecimalValue, instruction[13:16])
            RegisterFile().flagReset()
        #not complete
        elif (instruction[0:5] == "11110"):  # for compare have to set the flag register
            if (RegisterFile().getRegister(instruction[10:13],0) == RegisterFile().getRegister(instruction[13:16],0)):
                RegisterFile().updateRegister(1, "111")
            elif(RegisterFile().getRegister(instruction[10:13],0) > RegisterFile().getRegister(instruction[13:16],0)):
                RegisterFile().updateRegister(2, "111")
            else:
                RegisterFile().updateRegister(4, "111")
    def ISATypeD(self, instruction):
        if(instruction[0:5] == "10101"):
            RegisterFile().updateVariable(instruction[8:16], RegisterFile().getRegister(instruction[5:8],0))
            Memory.memoryPlotXCoordinates.append(ProgramCounter.cycleCounter)
            Memory.memoryPlotYCoordinates.append(getDecimal(instruction[8:16]))
            RegisterFile().flagReset()
        elif(instruction[0:5] == "10100"):
            RegisterFile().updateRegister(RegisterFile().getVariable(instruction[8:16]), instruction[5:8])
            Memory.memoryPlotXCoordinates.append(ProgramCounter.cycleCounter)
            Memory.memoryPlotYCoordinates.append(getDecimal(instruction[8:16]))
            RegisterFile().flagReset()
    def ISATypeE(self, instructions):
        if(instructions[0:5] == "11111"):  # for jump
            ProgramCounter.jumpSet=ProgramCounter.PCValue
            ProgramCounter.PCValue=getDecimal(instructions[8:16])
            RegisterFile().flagReset()
        elif(instructions[0:5] == "01100"):  # for jump if less than
            if(RegisterFile().getRegister("111",0)==4):
                ProgramCounter.jumpSet=ProgramCounter.PCValue
                ProgramCounter.PCValue=getDecimal(instructions[8:16])
            else:
                ProgramCounter.PCValue+=1
                ProgramCounter.jumpSet=-1
            RegisterFile().flagReset()
        elif(instructions[0:5] == "01101"):  # for jump if greater than
            if(RegisterFile().getRegister("111",0)==2):
                ProgramCounter.jumpSet=ProgramCounter.PCValue
                ProgramCounter.PCValue=getDecimal(instructions[8:16])
            else:
                ProgramCounter.jumpSet=-1
                ProgramCounter.PCValue+=1
            RegisterFile().flagReset()
        elif(instructions[0:5] == "01111"):  # for jump if equal
            if(RegisterFile().getRegister("111",0)==1):
                ProgramCounter.jumpSet=ProgramCounter.PCValue
                ProgramCounter.PCValue=getDecimal(instructions[8:16])
            else:
                ProgramCounter.jumpSet=-1
                ProgramCounter.PCValue+=1
            RegisterFile().flagReset()
    def execute(self, instruction):
        ProgramCounter.cycleCounter+=1
        Memory.memoryPlotXCoordinates.append(ProgramCounter.cycleCounter)
        Memory.memoryPlotYCoordinates.append(ProgramCounter.PCValue)
        if(instruction[0:5] == "10010"):
            self.ISATypeB(instruction)
            ProgramCounter.PCValue+=1
        elif(instruction[0:5] == "10011"):
            self.ISATypeC(instruction)
            ProgramCounter.PCValue+=1
        else:
            typeinstuction = self.getType(instruction[0:5])
            if typeinstuction == "A":
                ProgramCounter.jumpSet=-1
                ProgramCounter.PCValue+=1
                self.ISATypeA(instruction)
            elif typeinstuction == "B":
                ProgramCounter.jumpSet=-1
                self.ISATypeB(instruction)
                ProgramCounter.PCValue+=1
            elif typeinstuction == "C":
                ProgramCounter.jumpSet=-1
                self.ISATypeC(instruction)
                ProgramCounter.PCValue+=1
            elif typeinstuction == "D":
                ProgramCounter.jumpSet=-1
                self.ISATypeD(instruction)
                ProgramCounter.PCValue+=1
            elif typeinstuction == "E":
                self.ISATypeE(instruction)
            elif typeinstuction == "F":
                ProgramCounter.jumpSet=-1
                ProgramCounter.PCValue+=1
                ExecutionEngine.isHalt = True
        return ExecutionEngine.isHalt, ProgramCounter.PCValue
class Memory:
    memoryPlotXCoordinates = []
    memoryPlotYCoordinates = []
    def __init__(self):
        self.MEMORY = []
        self.FINAL_MEM = []
        self.dumpMemory=[]
    def initialize(self):
        for line in sys.stdin:
            self.MEMORY.append(line.rstrip())
    def getData(self, pc):
        return(self.MEMORY[pc])
    def dump(self):
        self.emptyLines = 256 - len(self.MEMORY)
        for line in self.MEMORY:
            self.dumpMemory.append(line)
        for emptyLine in range(self.emptyLines):
            varMem = getBinary(emptyLine+len(self.MEMORY))
            empty = "0" * (8 - len(varMem))
            final = empty + varMem
            if final in RegisterFile.allVariables.keys():
                binVar = getBinary(RegisterFile.allVariables[final])
                empty = "0" * (16 - len(binVar))
                final = empty + binVar
                self.dumpMemory.append(final)
            else:
                extra = ("0"*16)
                self.dumpMemory.append(extra)
        for line in range(len(self.dumpMemory)):
            print(self.dumpMemory[line])
        
    def length(self):
        return len(self.MEMORY)
    def __str__(self):
        return self.MEMORY[ProgramCounter]
    def plotMemory(self):
        pyplot.scatter(Memory.memoryPlotXCoordinates, Memory.memoryPlotYCoordinates, alpha=0.8)
        pyplot.xlabel('Cycle Number')
        pyplot.ylabel('Memory Address')
        pyplot.xticks(Memory.memoryPlotXCoordinates)
        pyplot.savefig('Memory.png')
