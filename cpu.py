"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.stack_pointer = 7 # dictated in the specs
        self.flags_register = 0

    def load(self):
        """Load a program into memory."""

        address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        with open(sys.argv[1], 'r') as program:
            for instruction in program:
                # print(instruction)
                if '#' in instruction:
                    instruction = instruction.split()[0]
                    if instruction == '#':
                        continue
                else:
                    instruction = instruction.replace('\n', '')
                if instruction != '':
                    self.ram[address] = int(instruction, 2)
                address += 1
            # print(self.ram)
                

    def ram_read(self, slot):
        return self.ram[slot]

    def ram_write(self, slot, val):
        self.ram[slot] = val
        
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_slot_1] < self.reg[reg_slot_2]:
                    self.flags_register = 0b00000100 # L
            elif self.reg[reg_slot_1] > self.reg[reg_slot_2]:
                self.flags_register = 0b00000010 # G
            else:
                self.flags_register = 0b00000001 # E
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True
        operations = {
            'HLT': 0b00000001,
            'LDI': 0b10000010,
            'PRN': 0b01000111,
            'MUL': 0b10100010,
            'PUSH': 0b01000101,
            'POP': 0b01000110,
            'CALL': 0b01010000,
            'RET': 0b00010001,
            'ADD': 0b10100000,
            'CMP': [0b00000100, 0b00000010, 0b00000001],
            'JMP': 0b01010100,
            'JEQ': 0b01010101,
            'JNE': 0b01010110
        }
        while running:
            instruction = self.ram_read(self.pc)
            if instruction == operations['HLT']:
                running = False
            elif instruction == operations['LDI']:
                reg_slot = self.ram[self.pc + 1]
                val = self.ram[self.pc + 2]
                self.reg[reg_slot] = val
                self.pc += 3
            elif instruction == operations['PRN']:
                reg_slot = self.ram[self.pc + 1]
                print(self.reg[reg_slot])
                self.pc += 2
            elif instruction == operations['MUL']:
                reg_slot_1 = self.ram[self.pc + 1]
                reg_slot_2 = self.ram[self.pc + 2]
                self.alu('MUL', reg_slot_1, reg_slot_2)
                self.pc += 3
            elif instruction == operations['PUSH']:
                self.reg[self.stack_pointer] -= 1
                reg_slot = self.ram[self.pc + 1]
                value = self.reg[reg_slot]
                new_value_address = self.reg[self.stack_pointer]
                self.ram[new_value_address] = value
                self.pc += 2
            elif instruction == operations['POP']:
                value_address = self.reg[self.stack_pointer]
                value = self.ram[value_address]
                reg_slot = self.ram[self.pc + 1]
                self.reg[reg_slot] = value
                self.reg[self.stack_pointer] += 1
                self.pc += 2
            elif instruction == operations['CALL']:
                self.reg[self.stack_pointer] -= 1
                return_address = self.pc + 2
                value_address = self.reg[self.stack_pointer]
                self.ram[value_address] = return_address
                reg_slot = self.ram[self.pc + 1]
                subroutine_address = self.reg[reg_slot]
                self.pc = subroutine_address
            elif instruction == operations['RET']:
                value_address = self.reg[self.stack_pointer]
                return_address = self.ram[value_address]
                self.reg[self.stack_pointer] += 1
                self.pc = return_address
            elif instruction == operations['ADD']:
                reg_slot_1 = self.ram[self.pc + 1]
                reg_slot_2 = self.ram[self.pc + 2]
                self.alu('ADD', reg_slot_1, reg_slot_2)
                self.pc += 3
            elif instruction in operations['CMP']:
                reg_slot_1 = self.ram[self.pc + 1]
                reg_slot_2 = self.ram[self.pc + 2]
                self.alu('CMP', reg_slot_1, reg_slot_2)
                self.pc += 3
            elif instruction == operations['JMP']:
                reg_slot = self.ram[self.pc + 1]
                self.pc = self.reg[reg_slot]
            elif instruction == operations['JEQ']:
                reg_slot = self.ram[self.pc + 1]
                if self.flags_register == 0b00000001:
                    self.pc = self.reg[reg_slot]
                else:
                    self.pc += 2
            elif instruction == operations['JNE']:
                reg_slot = self.ram[self.pc + 1]
                if self.flags_register != 0b00000001:
                    self.pc = self.reg[reg_slot]
                else:
                    self.pc += 2