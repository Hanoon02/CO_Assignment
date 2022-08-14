from Components import *
MEM = Memory()
RF = RegisterFile()
EE = ExecutionEngine()
PC = ProgramCounter()
MEM.initialize()
halted = False
while(not halted):
    Instruction = MEM.getData(PC.getValue())
    halted, nextPC = EE.execute(Instruction)
    PC.dump()
    RF.dump()
    PC.update(nextPC)
MEM.dump()
MEM.plotMemory()