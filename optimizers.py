import copy

# Each process search needs its own optimization. 

class PatchOptimizer:
    def __init__(self):
        pass

    def optimize(self, patch):
        return copy.deepcopy(patch)

# Optimization one: Group same name + prot patches together
class PatchGroupOptimizer(PatchOptimizer):

    def joinSimilar(self, procPatches):
        masterPatches = []
        lookup = {
        }
        for procPatch in procPatches: 
            mapName = procPatch["name"]
            if mapName not in lookup:
                lookup[mapName] = {}
            protLookup = lookup[mapName]
            mapProt = procPatch["prot"]
            # New protection so add it
            if mapProt not in protLookup:
                protLookup[mapProt] = len(masterPatches)
                masterPatches.append(procPatch) 
            else:
                mapIndex = protLookup[mapProt]
                masterProcPatch = masterPatches[mapIndex]
                masterProcPatch["patches"] += procPatch["patches"]
        return masterPatches

    def optimize(self, patch):
        patch = super().optimize(patch)
        for binName, procPatches in patch.items():
            patch[binName] = self.joinSimilar(procPatches)

        return patch

# Optimization two: Merge overlapping patches together.
class PatchOverlapOptimizer(PatchOptimizer):
    def combineSinglePatchSet(self, patches):
        if len(patches) < 2:
            return patches

        # Sort patches by offset
        patches.sort(key=lambda a: a[0])
        patch_summaries = [(patch[0], patch[0] + len(patch[1]), index) for index, patch in enumerate(patches)]
        patch_focus = patch_summaries[0]
        new_patches = [patches[0]]

        for patch_summary in patch_summaries[1:]:
            (start, end, index) = patch_summary
            # empty patch
            if start == end:
                continue
            (root_start, root_end, _) = patch_focus
            # patch is inbetween the root patch
            # can skip it
            if start >= root_end:
                # Distinct new root
                patch_focus = patch_summary
                new_patches.append(patches[index])
            elif end <= root_end:
                # Within current patch so skip
                pass
            else:
                # Remove part that isn't a child of 
                # and create new root
                adjustment = (root_end - start)
                new_start = root_end 
                new_end = new_start + adjustment
                patch_focus = (new_start, new_end, index)
                old_patch = patches[index]
                new_patch = [new_start]
                new_patch.append(old_patch[1][adjustment:])
                new_patch.append(old_patch[2][adjustment:])
                new_patch.append(old_patch[3])
                new_patches.append(new_patch)
        return new_patches


    def combineOverlapping(self, procPatches):
        for idx, procPatch in enumerate(procPatches):
           procPatch["patches"] = self.combineSinglePatchSet(procPatch["patches"])

    def optimize(self, patch):
        patch = super().optimize(patch)
        for binName, procPatches in patch.items():
            self.combineOverlapping(procPatches)
        return patch

# Optimization three: Minimize amount of necessary syscalls 
# Optimization four: Bulk read and bulk write by PS4 page size (0x4000) or less

