# Gen1 Tables

## basestats.yaml
Contains the Stats of every single Pokémon (in Dex order)

For each element:
Unless otherwise specified, references to tables are 1-based

| Field | Type | Contents | Example (Bulbasaur) |
|-------|------|----------|---------------------|
| `baseexp` | `int` | The base EXP number used for XP calculation after you defeat this Pokémon | `64` |
| `catchrate` | `int` | This states how easy a Pokémon is to catch. | `45` |
| `dexno` | `int` | National Pokédex Number | `1` |
| `startmoves` | 4-tuple of Attack IDs | 0 = no attack | `[33, 45, 0, 0]` |
| `stats` | 5-tuple of base stats | In this order: HP, Attack, Defense, Speed, Special | `[45, 49, 49, 45, 65]` |
| `tms` | `list` of `int` | Lists the TMs the Pokémon can learn. HMs come directly after TMs | `[3,6,8,9,10,20,21,22,31,32,33,34,44,50,51]` |
| `types` | 2-tuple of type IDs | If a type appears twice, Pokemon only has one type | `[22, 3]` |

## charset.yml
Contains a list of 256 entries containing the games charset. Note that some behaviour like "TXT_FAR" (0x17) has to be implemented in code

## effecttypes.yml
Contains a list of human-readable strings for the Attack Effect IDs.

## encounters.yaml
Contains a list of all possible random encounters in grass/water. Each element has two sub-elements. The first one is for encounters in tall grass, the other one is for encounters on water.

| field name | type | contents |
|------------|------|----------|
| `encounters` | `list` of the following type | is empty if `rate` is 0 (= There are no encounters), else it is 10 elements long |
| `rate` | `int` | Encounter rate in `rate`/256 |

| field name | type | contents |
|------------|------|----------|
| `level` | `int` | Level of the Pokémon in this Encounter Slot |
| `pokemon` | Internal Pokémon ID | The Pokémon |

## evolutions.yaml
Contains a list of all evolutions. Sorted after internal Pokémon ID. The Elements are a List, as some Pokémon have multiple evolutions. If the list is empty, the Pokémon has no Evolution

| field name | type | contents |
|------------|------|----------|
| `into` | Internal Pokémon ID | ID into which this Pokémon evolves |
| `level` | `int` | Level at which this Pokémon evolves. For `type`s other than `"level"` this should be 1. |
| `type` | one of `"level"`, `"item"`, `"trade"` | How this Pokémon evolves |
| `item` | Item ID | Item ID required to evolve this Pokémon. Only present with `type` `"item"` |

## index_to_dex.yaml
Contains a table for converting Internal Pokémon ID -> National Dex Number

## map_names.yml
Contains a list of human-*readable* map names.

## monnames.yaml
Contains a list of Pokémon names, sorted in internal order

## movenames.yaml
Contains a list of move names, sorted in internal order

## movesets.yaml
Contains a list of all moves learned for each Pokémon. Sorted after internal Pokémon ID. The Elements are a list, and they contain the following dict:

| field name | type | contents |
|------------|------|----------|
| `level` | `int` | Level this Pokémon learns the following move |
| `move` | move ID | The move it learns

## moves.yaml
Contains a list of all possible moves. 

| field name | type | contents | Example (pound) |
|------------|------|----------|-----------------|
| `accuracy` | `int` | Accuracy in `accuracy`/256 | `255` |
| `animation` | `int` | In these games synonymous to the move ID | `1` |
| `effect` | `str` | Human readable string describing the move's effect | `"No additional effect"` |
| `power` | `int` | Attack power of the move, as used by the damage calculation algorithm | `40` |
| `pp` | `int` | Maximum uses of this move, without PP-ups. Always a multiple of 5 | `35` |
| `type` | Type ID | Type of the move. | `0` |

## pokedex_ent.yaml
Contains all Pokédex entries. Sorted in internal order.

| field name | type | contents | Example (Rhydon) |
|------------|------|----------|------------------|
| `feet`     | `int` or `NoneType` | Is null/None if the game is not english. Otherwise it contains the size of the Pokémon in feet | `6` |
| `inches`   | `int` or `NoneType` | Is null/None if the game is not english. Otherwise it contains the remaining size of the Pokémon in inches | `3` |
| `kilograms` | `float` or `NoneType` | Is null/None if the game is english. Otherwise it contains the weight in kilograms | `17.6` (J) |
| `meters` | `float` or `NoneType` | Is null/None if the game is english. Otherwise it contains the height in meters | `1.9` (J) |
| `pounds` | `float` or `NoneType` | Is null/None if the game is not english. Otherwise it contains the weight of the Pokémon in pounds. | `26.5` |
| `speciesType` | `str` | Contains the Species of the Pokémon | `DRILL` |
| `text` | `str` | Contains the actual Pokédex text | `"Protected by an armor-like hide, it is capable of living in molten lava of 3,600 degrees"` |

## typenames.yaml
Contains a list of the type names.

