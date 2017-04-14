#!/usr/bin/env python3
import yaml
import struct

#Settings
#Feel free to change them
includeGlitch=False

f = open("game.gb","rb")
f.seek(0x41024)
indexToDex=[]
for i in range(0 if includeGlitch else 1, 256 if includeGlitch else 190):
    indexToDex.append(int.from_bytes(f.read(1), 'little'))
print("Writing internal id -> pokédex number mapping")
with open("index_to_dex.yaml","w") as f1:
    f1.write(yaml.dump(indexToDex,default_flow_style=False))

basestats=[]
def seek_to_stat(id):
    if id==151:
        f.seek(0x425B)
    else:
        id-=1
        if id < 0:
            id = 255
        f.seek(0x383DE+id*28)
f.seek(0x383DE)
def do_stats(pkID):
    seek_to_stat(pkID)
    dex = struct.unpack("<B",f.read(1))[0]
    stats = list(struct.unpack("<BBBBB",f.read(5)))
    types = list(struct.unpack("<BB",f.read(2)))
    catchrate = struct.unpack("<B",f.read(1))[0]
    baseexp = struct.unpack("<B",f.read(1))[0]
    startmoves = list(struct.unpack("<xxxxxBBBB",f.read(9)))
    growth = struct.unpack("<B",f.read(1))[0]
    tmsnum = int.from_bytes(f.read(7), byteorder="little")
    f.read(1)
    tms = [int(x) for x in bin(tmsnum)[2:]]
    basestats.append({"dexno":dex,"stats":stats,"types":types,"catchrate":catchrate,"baseexp":baseexp,"startmoves":startmoves,"tms":tms})

for i in sorted(list(set(indexToDex))):
    do_stats(i)
print("Writing pokémon base stats")
with open("basestats.yaml","w") as f1:
    f1.write(yaml.dump(basestats,default_flow_style=False))

def txt_to_str(bts):
    tbl = yaml.load(open("charset.yml","r").read())
    s = ""
    for c in bts:
        s=s+tbl[c]
    return s
def _get_text(maxlen=None):
    bts = b''
    cur = f.read(1)
    while cur != b'\x50' and cur != b'\x5F' and (True if maxlen == None else len(bts)<maxlen):
        if cur == b'':
            return bts
        if cur == b'\x17':
            #txt far
            offset,bank = struct.unpack("<HB",f.read(3))
            if bank != 0:
                offset -= 0x4000
                offset += bank * 0x4000
            pos = f.tell()
            f.seek(offset)
            bts = bts + _get_text(None if maxlen == None else maxlen-len(bts))
            f.seek(pos)
            cur=f.read(1)
        else:
            bts = bts + cur
            cur = f.read(1)
    return bts
def get_text(maxlen=None):
    return txt_to_str(_get_text(maxlen))

def get_type_name(id):
    f.seek(0x27DAE+id*2)
    off = struct.unpack("<H",f.read(2))[0]
    f.seek(0x20000+off)
    return get_text()

types=[]
for stat in basestats:
    types.append(stat["types"][0])
    types.append(stat["types"][1])
types = sorted(list(set(types)))
typenames = {}
for t in types:
    typenames[t]=get_type_name(t)
print("Writing typenames")
with open("typenames.yaml","w") as f1:
    f1.write(yaml.dump(typenames,default_flow_style=False))

def get_pokemon_name(id):
    f.seek(0x1C21E+id*10)
    return get_text(100)
names=[]
for i in range(0 if includeGlitch else 1, 256 if includeGlitch else 190):
    names.append(get_pokemon_name(i))
print("Writing pokémon names")
with open("monnames.yaml","w") as f1:
    f1.write(yaml.dump(names,default_flow_style=False))

def get_pokedex_entry(id):
    f.seek(0x4047E+id*2)
    off = int.from_bytes(f.read(2),'little')-0x4000
    f.seek(0x40000+off)
    speciesType = get_text(100)
    feet, inch, pounds = struct.unpack("<BBH",f.read(4))
    pokedexText = get_text(1000)
    return {"speciesType":speciesType,"feet":feet,"inchs":inch,"pounds":pounds,"meters":None,"kilograms":None,"text":pokedexText}

entries=[]
for i in range(0 if includeGlitch else 1, 256 if includeGlitch else 190):
    entries.append(get_pokedex_entry(i))
print("Writing pokédex entries")
with open("pokedex_ent.yaml", "w") as f1:
    f1.write(yaml.dump(entries,default_flow_style=False))
