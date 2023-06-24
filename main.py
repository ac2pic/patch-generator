#!/usr/bin/python3
from elf import *
from optimizers import *
import sys
import json

patch_fn = sys.argv[1]
with open(patch_fn, 'r') as fh:
    patch_data = json.load(fh)

def getPatchElfName(patch_data, entryName, index = 0):
    p = patch_data[entryName][index]
    if entryName == "":
        return p["name"]
    return entryName + ".elf"

fh = {}
def createElfFileHandle(elfName):
    if fh.get(elfName, None) != None:
        return fh.get(elfName)
    elfHandle = open(elfName, 'rb')
    fh[elfName] = elfHandle
    return elfHandle

def alignToMultiple(num, align):
    off = num % align
    if off != 0:
        num = (align - off) + num
    return num

def fixPatches(elfFh, elfName, patchSet):
    prot = patchSet["prot"]
    segment = ""
    if prot == 0b101:
        segment = ".text"
    elif prot == 0b110:
        segment = ".data"
    else:
        raise ValueError("Invalid protection " + str(prot))

    elf = Elf.parse(elfFh)    
    section = elf.get_section(segment)
    patchSet["size"] = alignToMultiple(section.p_memsz , section.p_align)
    for idx, patchEntry in enumerate(patchSet["patches"]):
        [offset, match, patch, comment ] = patchEntry
        offset = int(offset.replace(" ", ""), 16)

        patch = bytes.fromhex(patch.replace(" ", "").strip())
        matchLen = max(len(patch), 5)
        if section.p_filesz < matchLen:
            raise ValueError("filesize is too small")

        overflow = (offset + matchLen) - section.p_filesz
        adjustment = 0
        if overflow > 0:
            offset -= overflow
            adjustment += overflow

        patchEntry[0] = offset

        abs_offset = elf.section_off_to_abs_off(segment, offset)
        elfFh.seek(abs_offset)

        match = elfFh.read(matchLen)
        patchEntry[1] = match
        patchEntry[2] = bytes.fromhex(patchEntry[2].replace(" ", "").strip())
        if adjustment > 0:
            patchEntry[2] = match[0:adjustment] + patchEntry[2]

for binName, patches in patch_data.items():
    print(binName if len(binName) else "eboot.bin")
    for idx, patchSet in enumerate(patches):
        elfName = getPatchElfName(patch_data, binName, idx)
        print("elf:", elfName)
        elfHandle = createElfFileHandle(elfName)
        fixPatches(elfHandle, elfName, patchSet)
    # Close file handles
    for handle in fh.values():
        handle.close()
    fh.clear()

optimizers = [
        PatchGroupOptimizer(),
        PatchOverlapOptimizer()
]

for optimizer in optimizers:
    patch_data = optimizer.optimize(patch_data)

class PatchEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) == bytes:
            return obj.hex()
        return super().default(obj)

json.dump(patch_data,open("out.json", "w"),indent=4, cls=PatchEncoder)
