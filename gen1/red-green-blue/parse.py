#!/usr/bin/env python3
import yaml
import struct
import sys
import os
fname = sys.argv[1]
f = open(fname, "rb")
f.seek(0x014E)  # ROM CRC
foldertbl = {
    b'\x9d\x0a': "blue",
    b'\x91\xe6': "red",
    b'\xdd\xd5': "green-j",
    b'\xa2\xc1': "red-j",
    b'\xdc6':    "blue-j",
    b'\x3c\xa2': "blue-d",
    b'\x5c\xdc': "red-d",
    b'V\xa4':    "blue-f",
    b'z\xfc':    "red-f",
    b'^\x9c':    "blue-i",
    b'\x89\xd2': "red-i",
    b'\x14\xd7': "blue-e",
    b'8J':       "red-e"
}
os.chdir(foldertbl[f.read(2)])
with open("config.py", "r") as f2:
    exec(f2.read())

# Settings
# Feel free to change them
includeGlitch = False

f.seek(id_to_pokedex)
indexToDex = []
for i in range(0 if includeGlitch else 1,
               256 if includeGlitch else no_pokemon):
    indexToDex.append(int.from_bytes(f.read(1), 'little'))
print("Writing internal id -> pokédex number mapping")
with open("index_to_dex.yaml", "w") as f1:
    f1.write(
        yaml.dump(
            indexToDex,
            default_flow_style=False,
            allow_unicode=True))

basestats = []


def seek_to_stat(id):
    if id == 151:
        f.seek(mew_stat)
    else:
        id -= 1
        if id < 0:
            id = 255
        f.seek(other_stat + id * 28)


def do_stats(pkID):
    seek_to_stat(pkID)
    dex = struct.unpack("<B", f.read(1))[0]
    stats = list(struct.unpack("<BBBBB", f.read(5)))
    types = list(struct.unpack("<BB", f.read(2)))
    catchrate = struct.unpack("<B", f.read(1))[0]
    baseexp = struct.unpack("<B", f.read(1))[0]
    startmoves = list(struct.unpack("<xxxxxBBBB", f.read(9)))
    growth = struct.unpack("<B", f.read(1))[0]
    tmsnum = int.from_bytes(f.read(7), byteorder="little")
    f.read(1)
    tms = [int(x) for x in bin(tmsnum)[2:]]
    basestats.append({"dexno": dex,
                      "stats": stats,
                      "types": types,
                      "catchrate": catchrate,
                      "baseexp": baseexp,
                      "startmoves": startmoves,
                      "tms": tms})


for i in sorted(list(set(indexToDex))):
    if (i == 0) and not includeGlitch:
        continue
    do_stats(i)
print("Writing pokémon base stats")
with open("basestats.yaml", "w") as f1:
    f1.write(
        yaml.dump(
            basestats,
            default_flow_style=False,
            allow_unicode=True))


def txt_to_str(bts):
    tbl = yaml.load(open("charset.yml", "r").read())
    s = ""
    for c in bts:
        s = s + tbl[c]
    return s


def _get_text(maxlen=None):
    bts = b''
    cur = f.read(1)
    while cur != b'\x50' and cur != b'\x5F' and (
            True if maxlen is None else len(bts) < maxlen):
        if cur == b'':
            return bts
        if cur == b'\x17':
            # txt far
            offset, bank = struct.unpack("<HB", f.read(3))
            if bank != 0:
                offset -= 0x4000
                offset += bank * 0x4000
            pos = f.tell()
            f.seek(offset)
            bts = bts + \
                _get_text(None if maxlen is None else maxlen - len(bts))
            f.seek(pos)
            cur = f.read(1)
        else:
            bts = bts + cur
            cur = f.read(1)
    return bts


def get_text(maxlen=None):
    return txt_to_str(_get_text(maxlen))


def get_type_name(id):
    f.seek(type_nametbl + id * 2)
    off = struct.unpack("<H", f.read(2))[0]
    f.seek(type_nametblbank + off)
    return get_text()


types = []
for stat in basestats:
    types.append(stat["types"][0])
    types.append(stat["types"][1])
types = sorted(list(set(types)))
typenames = {}
for t in types:
    typenames[t] = get_type_name(t)
print("Writing typenames")
with open("typenames.yaml", "w") as f1:
    f1.write(
        yaml.dump(
            typenames,
            default_flow_style=False,
            allow_unicode=True))


def get_pokemon_name(id):
    f.seek(pkmn_nametbl + id * monnames_len)
    text = get_text(monnames_len)
    return text


names = []
for i in range(256 if includeGlitch else 190):
    names.append(get_pokemon_name(i))
print("Writing pokémon names")
with open("monnames.yaml", "w") as f1:
    f1.write(yaml.dump(names, default_flow_style=False, allow_unicode=True))


def get_pokedex_entry(id):
    f.seek(pkdex_tbl + id * 2)
    off = int.from_bytes(f.read(2), 'little') - 0x4000
    f.seek(pkdex_tblbank + off)
    speciesType = get_text(100)
    feet, inch, pounds, meters, kilograms = None, None, None, None, None
    if imperial:
        feet, inch, pounds = struct.unpack("<BBH", f.read(4))
        pounds /= 10
    else:
        meters, kilograms = struct.unpack("<BB", f.read(2))
        meters /= 10
        kilograms /= 10
    pokedexText = get_text(1000)
    return {
        "speciesType": speciesType,
        "feet": feet,
        "inchs": inch,
        "pounds": pounds,
        "meters": meters,
        "kilograms": kilograms,
        "text": pokedexText}


entries = []
for i in range(0, 256 if includeGlitch else 190):
    entries.append(get_pokedex_entry(i))
print("Writing pokédex entries")
with open("pokedex_ent.yaml", "w") as f1:
    f1.write(yaml.dump(entries, default_flow_style=False, allow_unicode=True))


def get_encounters(id):
    f.seek(encounters_tbl + id * 2)
    off = int.from_bytes(f.read(2), 'little')
    f.seek(encounters_tblbank + off)

    def get_rate():
        rate = struct.unpack("<B", f.read(1))[0]
        if rate == 0:
            encounters = []
        else:
            encounters = []
            for i in range(10):
                level, pokemon = struct.unpack("<BB", f.read(2))
                encounters.append({"level": level, "pokemon": pokemon})
        return rate, encounters
    grassRate, grassEncounters = get_rate()
    waterRate, waterEncounters = get_rate()
    return [{"rate": grassRate, "encounters": grassEncounters},
            {"rate": waterRate, "encounters": waterEncounters}]


# Maps
encounters = []
for i in range(248):
    encounters.append(get_encounters(i))

print("writing encounters")
with open("encounters.yaml", "w") as f1:
    f1.write(
        yaml.dump(
            encounters,
            default_flow_style=False,
            allow_unicode=True))

#Evos and moves


def get_evos_and_moves(id):
    f.seek(evos_tbl + id * 2)
    off = int.from_bytes(f.read(2), 'little') - 0x4000
    f.seek(evos_tblbank + off)

    def get_evos():
        evos = []
        typ = f.read(1)
        while typ != b'\x00':
            if typ == b'\x01':
                level, pokemon = struct.unpack("<BB", f.read(2))
                evos.append({"type": "level", "level": level, "into": pokemon})
            elif typ == b'\x02':
                item, level, pokemon = struct.unpack("<BBB", f.read(3))
                evos.append({"type": "item", "item": item,
                             "level": level, "into": pokemon})
            else:
                level, pokemon = struct.unpack("<BB", f.read(2))
                evos.append({"type": "trade", "level": level, "into": pokemon})
            typ = f.read(1)
        return evos

    def get_moves():
        moves = []
        while True:
            level, move = struct.unpack("<BB", f.read(2))
            if level == 0:
                break
            moves.append({"level": level, "move": move})
        return moves
    evos=get_evos()
    return {"evos": evos, "moves": get_moves()}


movesets = []
evols = []
for i in range(256 if includeGlitch else 190):
    x = get_evos_and_moves(i)
    movesets.append(x["moves"])
    evols.append(x["evos"])
print("Writing movesets and evos")
with open("movesets.yaml", "w") as f1:
    f1.write(yaml.dump(movesets, default_flow_style=False, allow_unicode=True))
with open("evolutions.yaml", "w") as f1:
    f1.write(yaml.dump(evols, default_flow_style=False, allow_unicode=True))

move_desc = None
with open("effecttypes.yml") as f1:
    move_desc = yaml.load(f1.read())
moves = []
f.seek(move_tbl)
for i in range(165):
    animation, effect, power, typ, accuracy, pp = struct.unpack(
        "<BBBBBB", f.read(6))
    moves.append({"animation": animation,
                  "effect": move_desc[effect],
                  "power": power,
                  "type": typ,
                  "accuracy": accuracy,
                  "pp": pp})

print("Writing move data")
with open("moves.yaml", "w") as f1:
    f1.write(yaml.dump(moves, default_flow_style=False, allow_unicode=True))

movenames = []
f.seek(move_nametbl)
for i in range(165):
    movenames.append(get_text())

print("Writing move names")
with open("movenames.yaml", "w") as f1:
    f1.write(
        yaml.dump(
            movenames,
            default_flow_style=False,
            allow_unicode=True))
