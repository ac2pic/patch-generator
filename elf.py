import struct

# ELF header structure

ELF_HEADER_FORMAT = '16s' # e_ident
ELF_HEADER_FORMAT += 'H' # e_type
ELF_HEADER_FORMAT += 'H' # e_machine
ELF_HEADER_FORMAT += 'I' # e_version
ELF_HEADER_FORMAT += 'Q' # e_entry
ELF_HEADER_FORMAT += 'Q' # e_phoff
ELF_HEADER_FORMAT += 'Q' # e_shoff
ELF_HEADER_FORMAT += 'IHHHHHH'


class ElfHeader:
    def __init__(self, data):
        (self.e_ident, self.e_type, self.e_machine, self.e_version,
         self.e_entry, self.e_phoff, self.e_shoff, self.e_flags,
         self.e_ehsize, self.e_phentsize, self.e_phnum, self.e_shentsize,
         self.e_shnum, self.e_shstrndx) = struct.unpack(ELF_HEADER_FORMAT, data)

    @staticmethod
    def parse(file):
        file.seek(0)
        data = file.read(0x40)  # Read the first 64 bytes (ELF header size)
        return ElfHeader(data)

    def print(self):
        # Print the parsed ELF header information
        print("ELF Header:")
        print("  Magic: ", self.e_ident[:4])
        print("  Class: ", '32-bit' if self.e_ident[4] == 1 else '64-bit')
        print("  Data: ", 'Little-endian' if self.e_ident[5] == 1 else 'Big-endian')
        print("  Version: ", self.e_ident[6])
        print("  Type: ", self.e_type)
        print("  Machine: ", self.e_machine)
        print("  Entry point address: ", hex(self.e_entry))
        print("  Program header offset: ", self.e_phoff)
        print("  Section header offset: ", self.e_shoff)
        print("  Flags: ", hex(self.e_flags))
        print("  ELF header size: ", self.e_ehsize)
        print("  Program header entry size: ", self.e_phentsize)
        print("  Number of program headers: ", self.e_phnum)
        print("  Section header entry size: ", self.e_shentsize)
        print("  Number of section headers: ", self.e_shnum)
        print("  Section header string table index: ", self.e_shstrndx)
        print()



# ELF program header structure
ELF_PROGRAM_HEADER_FORMAT = ''
ELF_PROGRAM_HEADER_FORMAT += 'I' # p_type
ELF_PROGRAM_HEADER_FORMAT += 'I' # p_flags
ELF_PROGRAM_HEADER_FORMAT += 'Q' # p_offset
ELF_PROGRAM_HEADER_FORMAT += 'Q' # p_vaddr
ELF_PROGRAM_HEADER_FORMAT += 'Q' # p_paddr
ELF_PROGRAM_HEADER_FORMAT += 'Q' # p_filesz
ELF_PROGRAM_HEADER_FORMAT += 'Q' # p_memsz
ELF_PROGRAM_HEADER_FORMAT += 'Q' # p_align

# Program header type constants
PT_NULL = 0
PT_LOAD = 1
PT_DYNAMIC = 2
PT_INTERP = 3
PT_NOTE = 4
PT_SHLIB = 5
PT_PHDR = 6
PT_TLS = 7
PT_NUM = 8
PT_LOOS = 0x60000000
PT_GNU_EH_FRAME = 0x6474e550
PT_GNU_STACK = 0x6474e551
PT_GNU_RELRO = 0x6474e552
PT_LOSUNW = 0x6ffffffa
PT_SUNWBSS = 0x6ffffffa
PT_SUNWSTACK = 0x6ffffffb
PT_HISUNW = 0x6fffffff
PT_HIOS = 0x6fffffff
PT_LOPROC = 0x70000000
PT_HIPROC = 0x7fffffff

# Program header flags constants
PF_X = 1 << 0
PF_W = 1 << 1
PF_R = 1 << 2
PF_MASKOS = 0x0ff00000
PF_MASKPROC = 0xf0000000

# Class to represent the ELF program header
class ElfProgramHeader:
    def __init__(self, data):
        (self.p_type, self.p_flags, self.p_offset, self.p_vaddr,
         self.p_paddr, self.p_filesz, self.p_memsz, self.p_align) = struct.unpack(ELF_PROGRAM_HEADER_FORMAT, data)

    @staticmethod
    def parse(file, header):
        file.seek(0x40)
        progHeaders = []
        # Read and parse each program header
        file.seek(header.e_phoff)
        for _ in range(header.e_phnum):
            data = file.read(header.e_phentsize)
            progHeaders.append(ElfProgramHeader(data))
        return progHeaders

    def get_p_type_string(self):
        p_type = self.p_type
        if p_type == PT_NULL:
            return 'PT_NULL'
        elif p_type == PT_LOAD:
            return 'PT_LOAD'
        elif p_type == PT_DYNAMIC:
            return 'PT_DYNAMIC'
        elif p_type == PT_INTERP:
            return 'PT_INTERP'
        elif p_type == PT_NOTE:
            return 'PT_NOTE'
        elif p_type == PT_SHLIB:
            return 'PT_SHLIB'
        elif p_type == PT_PHDR:
            return 'PT_PHDR'
        elif p_type == PT_TLS:
            return 'PT_TLS'
        elif p_type == PT_NUM:
            return 'PT_NUM'
        elif p_type == PT_LOOS:
            return 'PT_LOOS'
        elif p_type == PT_GNU_EH_FRAME:
            return 'PT_GNU_EH_FRAME'
        elif p_type == PT_GNU_STACK:
            return 'PT_GNU_STACK'
        elif p_type == PT_GNU_RELRO:
            return 'PT_GNU_RELRO'
        elif p_type == PT_LOSUNW:
            return 'PT_LOSUNW'
        elif p_type == PT_SUNWBSS:
            return 'PT_SUNWBSS'
        elif p_type == PT_SUNWSTACK:
            return 'PT_SUNWSTACK'
        elif p_type == PT_HISUNW:
            return 'PT_HISUNW'
        elif p_type == PT_HIOS:
            return 'PT_HIOS'
        elif p_type == PT_LOPROC:
            return 'PT_LOPROC'
        elif p_type == PT_HIPROC:
            return 'PT_HIPROC'
        else:
            return f'Unknown ({hex(p_type)})'

    # Function to convert program header flags to strings
    def get_p_flags_string(self):
        p_flags = self.p_flags
        flags = []
        if p_flags & PF_R:
            flags.append('R')
        else:
            flags.append('_')
        if p_flags & PF_W:
            flags.append('W')
        else:
            flags.append('_')
        if p_flags & PF_X:
            flags.append('X')
        else:
            flags.append('_')
        if p_flags & PF_MASKOS:
            flags.append('OS-specific ')
        if p_flags & PF_MASKPROC:
            flags.append('Processor-specific ')
        return ''.join(flags)

    def print(self):
        # Print the parsed program header information
        print("Program Header:")
        print("  Type: ", self.get_p_type_string())
        print("  Flags: ", self.get_p_flags_string())
        print("  Offset: ", hex(self.p_offset))
        print("  Virtual Address: ", hex(self.p_vaddr))
        print("  Physical Address: ", hex(self.p_paddr))
        print("  File Size: ", hex(self.p_filesz))
        print("  Memory Size: ", hex(self.p_memsz))
        print("  Alignment: ", hex(self.p_align))
        print()

            

# Example usage

class Elf:
    def __init__(self):
        self.header = None
        self.progHeaders = []
        self.sections = {}
    @staticmethod
    def parse(fh):
        elf = Elf() 
        header = ElfHeader.parse(fh)
        elf.header = header
        elf.progHeaders = ElfProgramHeader.parse(fh, header)
        for progHeader in elf.progHeaders:
            if progHeader.p_type == PT_LOAD:
                if progHeader.p_flags == 0b101:
                    elf.sections[".text"] = progHeader
                elif progHeader.p_flags == 0b110:
                    elf.sections[".data"] = progHeader
        return elf

    def print(self):
        self.header.print()
        for progHeader in self.progHeaders:
            progHeader.print()
        for key, section in self.sections.items():
            print(key, hex(section.p_offset), hex(section.p_filesz))

    def get_section(self, sectionName):
        section = self.sections.get(sectionName, None)
        if section == None:
            raise ValueError(sectionName + " doesn't exist")
        return section
    def section_off_to_abs_off(self, sectionName, offset):
        section = self.get_section(sectionName)
        if section.p_filesz <= offset:
            raise ValueError(hex(offset) + " is greater than filesize (" + hex(section.p_filesz) + ")")
        return section.p_offset + offset
