import math
class Memory:
    
    memorySizeNotations = {"KB":"13", "MB":"23", "GB":"33", "Kb": 10, "Mb": 20, "Gb": 30}

    def __init__(self, size, addressType):
        self.memorySize = size
        self.addressTypeChoice = addressType
        self.CPUBits=0

    def getAddressBits(self):
        self.integerBits = math.ceil(math.log(int(self.memorySize[:-2]), 2))
        self.sizeBits = int(Memory.memorySizeNotations[self.memorySize[-2:]])
        if(self.addressTypeChoice!=4):
            return (self.integerBits + self.sizeBits)-self.addressTypeChoice
        else:
            return (self.integerBits + self.sizeBits)-math.ceil(math.log(int(self.CPUBits), 2))
    
    def calculateMemorySize(self,pins):
        if(self.addressTypeChoice!=4):
            totalPower = pins + self.addressTypeChoice
        else:
            totalPower = pins + math.ceil(math.log(int(self.CPUBits), 2))
        if(totalPower>33):
            remainingPower=totalPower-33
            self.memorySize = str(2**remainingPower)+"GB"
        elif(totalPower>30):
            remainingPower=totalPower-30
            self.memorySize = str(2**remainingPower)+"Gb"
        elif(totalPower>23):
            remainingPower=totalPower-23
            self.memorySize = str(2**remainingPower)+"MB"
        elif(totalPower>20):
            remainingPower=totalPower-20
            self.memorySize = str(2**remainingPower)+"Mb"
        elif(totalPower>13):
            remainingPower=totalPower-13
            self.memorySize = str(2**remainingPower)+"KB"
        elif(totalPower>10):
            remainingPower=totalPower-10
            self.memorySize = str(2**remainingPower)+"Kb"
        else:
            self.memorySize = str(2**totalPower)+"B"
            
    def initializeCPUBits(self, bits):
        self.CPUBits = bits

class Instructions:
    typeA = {}
    typeB = {}

    def __init__(self, instructionLength, registerLength):
        self.instructionLength = instructionLength
        self.registerLength = registerLength

    def defineTypeA(self,addressSize):
        self.opBitSize = self.instructionLength - addressSize - self.registerLength
        Instructions.typeA["op"] = self.opBitSize
        Instructions.typeA["address"] = addressSize
        Instructions.typeA["register"] = self.registerLength
    
    def defineTypeB(self):
        Instructions.typeB["op"] = Instructions.typeA["op"]
        fillerBits = self.instructionLength - Instructions.typeA["op"] - 2*(self.registerLength)
        Instructions.typeB["filler"] = fillerBits
        Instructions.typeB["register1"] = self.registerLength
        Instructions.typeB["register2"] = self.registerLength
#------------------------------------------------------------------------------------------#
# Print Statements
    
print("="*100)
print("="*100)
print(("Memory Mumbo Jumbo").center(100))
print("="*100)
print("="*100)
print()


#------------------------------------------------------------------------------------------#
# Operations
memorySpace = input("Enter the memory space: ")
memoryAdress = int(input("Choose how memory adress is stored: \n1.Bit Addressable Memory\n2.Nibble Addressable Memory\n3.Byte Addressable Memory\n4.Word Addressable Memory\nEnter: "))
memory = Memory(memorySpace, memoryAdress)
#------------------------------------------------------------------------------------------#
# Print Statements

print()
print("="*100)
print(("ISA and Instructions").center(100))
print("="*100)
print()


#------------------------------------------------------------------------------------------#
# Operations
instructionLength = int(input("Enter the instruction length: "))
registerLength = int(input("Enter the register length: "))
instruction = Instructions(instructionLength, registerLength)
minBitsAddress = memory.getAddressBits()
instruction.defineTypeA(minBitsAddress)
instruction.defineTypeB()
opCodeBits = Instructions.typeA["op"]
fillerBits = Instructions.typeB["filler"]
maxInstructionCount = 2**(opCodeBits)
maxRegisterCount = 2**(instruction.registerLength)
#------------------------------------------------------------------------------------------#
# Print Statements

print()
print(("Here are your query answers").center(100))
print("1. Minimum number of bits required to store the address: " + str(minBitsAddress))
print("2. Bits for OP code: " + str(opCodeBits))
print("3. Bits for filler: " + str(fillerBits))
print("4. Maximum number of instructions: " + str(maxInstructionCount))
print("5. Maximum number of registers: " + str(maxRegisterCount))
print()

print("="*100)
print(("System Enhancement").center(100))
print("="*100)
print()
print(("Type 1").center(100))
print()


#------------------------------------------------------------------------------------------#
# Operations
cpuBits = int(input("Enter the number of bits in the CPU: "))
newMemoryAddress = int(input("How would you like to change the memory address type to? : \n1.Bit Addressable Memory\n2.Nibble Addressable Memory\n3.Byte Addressable Memory\n4.Word Addressable Memory\nEnter: "))
newMemory = Memory(memorySpace, newMemoryAddress)
newMemory.initializeCPUBits(cpuBits)
newMinBitsAddress = newMemory.getAddressBits()
pinChange = newMinBitsAddress-minBitsAddress
#------------------------------------------------------------------------------------------#  
# Print Statements

print()
print(("Here are your query answers").center(100))
print(pinChange)

print()
print(("Type 2").center(100))
print()


#------------------------------------------------------------------------------------------#
# Operations
cpuNewBits = int(input("Enter the number of bits in the CPU: "))
addressPinCount = int(input("Enter the number of address pins: "))
memoryAddressAgain = int(input("How would you like to change the memory address type to? : \n1.Bit Addressable Memory\n2.Nibble Addressable Memory\n3.Byte Addressable Memory\n4.Word Addressable Memory\nEnter: "))
finalMemory = Memory(0, memoryAddressAgain)
finalMemory.initializeCPUBits(cpuNewBits)
finalMemory.calculateMemorySize(addressPinCount)
finalMemorySize = finalMemory.memorySize
#------------------------------------------------------------------------------------------#
# Print Statements

print()
print(("Here are your query answers").center(100))
print(finalMemorySize)
print()

print("="*100)
print(("Exiting Program").center(100))
print("="*100)
