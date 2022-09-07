#!/usr/bin/env python

#NAME: Cao Xu
#EMAIL: cxcharlie@gmail.com
#ID: 704551688

from __future__ import print_function
import sys, csv

class Superblock:
    def __init__(self, a, b, c, d, e, f, g): #THE 8 PARAMATERS AS LISTED IN P3A
        self.n_blocks = int(a)
        self.n_inodes = int(b)
        self.block_size = int(c)
        self.inode_size = int(d)
        self.bpg = int(e)
        self.ipg = int(f)
        self.first = int(g)

class Group:
    def __init__(self, a, b, c, d, e, f, g, h):
        self.group_num = int(a)
        self.n_blocks = int(b)
        self.n_inodes = int(c)
        self.f_blocks = int(d)
        self.f_inodes = int(e)
        self.f_block_bitmap = int(f)
        self.f_inode_bitmap = int(g)
        self.first_iblock = int(h)

#didn't include Bfree and Ifree because they have 1 paramater and more
#simple to not include entire class

class Inode:
    def __init__(self, a, b, c, d, e, f, g, h, i, j, k):
        self.inum = int(a)
        self.type = b
        self.mode = c
        self.owner = int(d)
        self.group = int(e)
        self.n_links = int(f)
        self.t_inode_change = g
        self.t_modification = h
        self.t_access = i
        self.file_size = int(j)
        self.blocks_used = int(k)

class Dirent:
    def __init__(self, a, b, c, d, e, f):
        self.parent_inum = int(a)
        self.offset = int(b)
        self.inum = int(c)
        self.entry_length = int(d)
        self.name_length = int(e)
        self.name = f

class Indirect:
    def __init__(self, a, b, c, d, e):
        self.inum = int(a)
        self.level = int(b)
        self.offset = int(c)
        self.indirect_bnum = int(d)
        self.direct_bnum = int(e)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.exit(1)

def main():
    incons = False
    if len(sys.argv) != 2: #Argument 0 is reserved for script name
        eprint("Error occurred: Invalid number of arguments.")

    superr = None
    groupp = None
    bfree_list = set()
    ifree_list = set()
    ilist = []
    ilist2 = [] #REPLACE ilist with ilist2 if rest of inode not used!!!!!!!!!!!!!!!!!
    dlist = []
    holder = {}
    first_non_reserved = -1
    inodetolink = {}
    inodetoparent = {}
    
    try:
        with open(sys.argv[1], "r") as f:
            reader = csv.reader(f)
            for line in reader:
                if line[0] == 'SUPERBLOCK':
                    superr = Superblock(line[1], line[2], line[3], line[4], line[5], line[6], line[7])
                elif line[0] == 'GROUP':
                    groupp = Group(line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8])
                elif line[0] == 'BFREE':
                    bfree_list.add(int(line[1]))
                elif line[0] == 'IFREE':
                    ifree_list.add(int(line[1]))
                elif line[0] == 'DIRENT':
                    dlist.append(Dirent(line[1], line[2], line[3], line[4], line[5], line[6]))
            
            first_non_reserved = int(groupp.first_iblock + superr.inode_size * groupp.n_inodes / superr.block_size) #ASSUME SUPERBLOCK DONE
            for i in range(first_non_reserved, superr.n_blocks):
                holder.update({i: []})

            f.seek(0)
            reader = csv.reader(f)
            for line in reader:
                if line[0] == 'INODE':
                    ino = Inode(line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10], line[11])
                    ilist.append(ino)
                    ilist2.append(int(line[1]))

                    for i in range(12, 27):
                        block_number = int(line[i])
                        if block_number == 0: #don't care about these
                            continue 
                        if block_number < 0 or block_number > superr.n_blocks: #OUT OF RANGE INVALID
                            incons = True
                            if i == 24:
                                print("INVALID INDIRECT BLOCK {} IN INODE {} AT OFFSET 12".format(block_number, line[1]))
                            elif i == 25:
                                print("INVALID DOUBLE INDIRECT BLOCK {} IN INODE {} AT OFFSET 268".format(block_number, line[1]))
                            elif i == 26:
                                print("INVALID TRIPLE INDIRECT BLOCK {} IN INODE {} AT OFFSET 65804".format(block_number, line[1]))
                            else:
                                print("INVALID BLOCK {} IN INODE {} AT OFFSET {}".format(block_number, line[1], str(i-12)))
                        elif (block_number < first_non_reserved):
                            incons = True
                            if i == 24:
                                print("RESERVED INDIRECT BLOCK {} IN INODE {} AT OFFSET 12".format(block_number, line[1]))
                            elif i == 25:
                                print("RESERVED DOUBLE INDIRECT BLOCK {} IN INODE {} AT OFFSET 268".format(block_number, line[1]))
                            elif i ==26:
                                print("RESERVED TRIPLE INDIRECT BLOCK {} IN INODE {} AT OFFSET 65804".format(block_number, line[1]))
                            else:
                                print("RESERVED BLOCK {} IN INODE {} AT OFFSET {}".format(block_number, line[1], str(i-12)))
                        else:
                            x = 0
                            if i == 24:
                                x = 12
                            elif i == 25:
                                x = 268
                            elif i == 26:
                                x = 65804
                            else:
                                x = i-12
                            if (i == 24):
                                holder[block_number].append([int(line[1]), 12, 1])
                            elif (i == 25):
                                holder[block_number].append([int(line[1]), 268, 2])
                            elif (i == 26):
                                holder[block_number].append([int(line[1]), 65804, 3])
                            else:
                                holder[block_number].append([int(line[1]), i-12, 0])

                elif line[0] == 'INDIRECT':
                    #indlist.append(Indirect(line[1], line[2], line[3], line[4], line[5]))
                    block_number = int(line[5])

                    #if block_number == 0
                    lvl = int(line[2])

                    if (block_number < 0 or block_number > superr.n_blocks):
                        incons = True
                        if (lvl == 1):
                            print("INVALID INDIRECT BLOCK {} IN INODE {} AT OFFSET {}".format(block_number, line[1], line[3]))
                        elif (lvl == 2):
                            print("INVALID DOUBLE INDIRECT BLOCK {} IN INODE {} AT OFFSET {}".format(block_number, line[1], line[3]))
                        elif (lvl == 3):
                            print("INVALID DOUBLE INDIRECT BLOCK {} IN INODE {} AT OFFSET {}".format(block_number, line[1], line[3]))
                    elif (block_number < first_non_reserved):
                        incons = True
                        if (lvl == 1):
                            print("RESERVED INDIRECT BLOCK {} IN INODE {} AT OFFSET {}".format(block_number, line[1], line[3]))
                        elif (lvl == 2):
                            print("RESERVED DOUBLE INDIRECT BLOCK {} IN INODE {} AT OFFSET {}".format(block_number, line[1], line[3]))
                        elif (lvl == 3):
                            print("RESERVED DOUBLE INDIRECT BLOCK {} IN INODE {} AT OFFSET {}".format(block_number, line[1], line[3]))
                    else:
                        if (lvl == 1):
                            holder[block_number].append([int(line[1]), 12, 1])
                        elif (lvl == 2):
                            holder[block_number].append([int(line[1]), 268, 2])
                        elif (lvl == 3):
                            holder[block_number].append([int(line[1]), 65804, 3])
    except IOError:
        eprint("I/O error occurred while opening");
    except IndexError:
        eprint("Index Error occurred!");
    except:
        eprint("Some other error occurred IDK lol u figure it out");

    for i in holder:
        if len(holder[i]) > 0 and i in bfree_list:
            incons = True
            print("ALLOCATED BLOCK {} ON FREELIST".format(str(i)))
        elif len(holder[i]) == 0 and i not in bfree_list:
            incons = True
            print("UNREFERENCED BLOCK {}".format(str(i)))
        if len(holder[i]) > 1:
            incons = True
            for j in holder[i]:
                if j[2] == 0:
                    print("DUPLICATE BLOCK {} IN INODE {} AT OFFSET {}".format(str(i), str(j[0]), str(j[1])))
                elif j[2] == 1:
                    print("DUPLICATE INDIRECT BLOCK {} IN INODE {} AT OFFSET {}".format(str(i), str(j[0]), str(j[1])))
                elif j[2] == 2:
                    print("DUPLICATE DOUBLE INDIRECT BLOCK {} IN INODE {} AT OFFSET {}".format(str(i), str(j[0]), str(j[1])))
                elif j[2] == 3:
                    print("DUPLICATE TRIPLE INDIRECT BLOCK {} IN INODE {} AT OFFSET {}".format(str(i), str(j[0]), str(j[1])))

    #I-Node Allocation Audit
    for inode in ilist:
        x = inode.inum
        if x > 0 and x in ifree_list:
            incons = True
            print("ALLOCATED INODE {} ON FREELIST".format(str(x)))

    for inode in range(superr.first, groupp.n_inodes): #cant iterate thru ilist cuz could be some not documented by .csv
        if inode not in ifree_list and inode not in ilist2:
            incons = True
            print("UNALLOCATED INODE {} NOT ON FREELIST".format(str(inode)))

    #Directory Consistency Audit

    #Initialization Step
    for i in range(1, superr.n_inodes + 1):
        inodetolink[i] = 0
    
    for i in range(len(dlist)):
        inodetoparent[i] = 0
    
    inodetoparent[2] = 2 #Root directory's parent is itself, inode 2 is /

    for dirr in dlist:
        x = dirr.inum
        if x < 1 or x > superr.n_inodes:
            incons = True
            print("DIRECTORY INODE {} NAME {} INVALID INODE {}".format(str(dirr.parent_inum), dirr.name, str(x)))
        elif x not in ilist2:
            incons = True
            print("DIRECTORY INODE {} NAME {} UNALLOCATED INODE {}".format(str(dirr.parent_inum), dirr.name, str(x)))
        else:
            inodetolink[x] += 1

        if dirr.name != "'.'" and dirr.name != "'..'":
            inodetoparent[x] = dirr.parent_inum

    for dirr in dlist:
        if dirr.name == "'.'" and dirr.parent_inum != dirr.inum:
            incons = True
            print("DIRECTORY INODE {} NAME '.' LINK TO INODE {} SHOULD BE {}".format(str(dirr.parent_inum), str(dirr.inum), str(dirr.parent_inum)))
        if dirr.name == "'..'" and int(inodetoparent[dirr.parent_inum]) != dirr.inum:
            incons = True
            print("DIRECTORY INODE {} NAME '..' LINK TO INODE {} SHOULD BE {}".format(str(dirr.parent_inum), str(dirr.inum), str(inodetoparent[dirr.parent_inum]))) 
    
    #Finally we compare if the link count is correct
    for inode in ilist:
        x = inode.inum
        if int(inodetolink[x]) != inode.n_links:
            incons = True
            print("INODE {} HAS {} LINKS BUT LINKCOUNT IS {}".format(str(x), str(inodetolink[x]), str(inode.n_links)))

    f.close()

    if incons:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
