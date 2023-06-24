import unittest
import sys
sys.path.append('..')
from optimizers import *

def createPatchSet(name, prot, patches):
    return {
        "name": name,
        "prot": prot,
        "patches": patches
    }
def createPatch(offset, match, patch, comment = ""):
    return [offset, match, patch, comment]
class Testing(unittest.TestCase):
    def test_group_optimizer(self):
        c = []
        d = []

        for i in range(0, 5):
            baseNum = i * 4
            patch = createPatch(baseNum, "", "", "A patch for " + str(i))
            c.append(createPatchSet("exec", 5, [patch]))
            d.append(patch)
    
        patch_input = {"": c}
        patch_output = {"": [createPatchSet("exec", 5, d)]}
    
        out = PatchGroupOptimizer().optimize(patch_input)
        self.assertDictEqual(out, patch_output)
    
    def test_overlapping_optimizer_contained(self):
        offset = 0
        patch = b'AB'
    
        d = []
        for idx in range(len(patch)):
            length = len(patch) - idx
            d.append(createPatch(idx, patch[idx:length], b"\x00" * length, "Patch at " + str(idx)))
        #      0   1
        #1:    AB CD
        #
        #2:    CD 
        patch_input = {"": [createPatchSet("", 0, d)]}
        #      0   1
        #1:    AB CD
        patch_output = {"": [createPatchSet("", 0, d[0:1])]}
        out = PatchOverlapOptimizer().optimize(patch_input)
        self.assertDictEqual(out, patch_output)

    def test_overlapping_optimizer_intersecting(self):
        offset = 0
        patch = b'AB'
    
        d = [
            createPatch(0, b"\x00", b"\x00", "Patch at " + str(1)),
            createPatch(0, b"\x00\x01", b"\x00\x02", "Patch at " + str(2))
        ]
        #      0  1
        #1:    AB
        #
        #2:    AB CD
        patch_input = {"": [createPatchSet("", 0, d)]}
        #      0  1
        #1:    AB
        #2:       CD 
        e = [
            createPatch(0, b"\x00", b"\x00", "Patch at " + str(1)),
            createPatch(1, b"\x01", b"\x02", "Patch at " + str(2))
        ]
        patch_output = {"": [createPatchSet("", 0, e)]}
        out = PatchOverlapOptimizer().optimize(patch_input)
        self.assertDictEqual(out, patch_output)
    def test_overlapping_optimizer_notoverlapping(self):
        e = [
            createPatch(0, b"\x00", b"\x00", "Patch at " + str(1)),
            createPatch(1, b"\x01", b"\x02", "Patch at " + str(2))
        ]
        patch_input = {"": [createPatchSet("", 0, e)]}
        patch_output = patch_input
        out = PatchOverlapOptimizer().optimize(patch_input)
        self.assertDictEqual(out, patch_output)

if __name__ == '__main__':
    unittest.main()
