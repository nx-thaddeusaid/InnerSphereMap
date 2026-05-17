# InnerSphereMap

A [ModTek](https://github.com/BattletechModders/ModTek) mod for [HBS BattleTech](https://harebrained-schemes.com/battletech/) that replaces the game's small campaign map with the full Inner Sphere — over 4,700 star systems across multiple eras.

**Upstream repo:** [wmtorode/InnerSphereMap](https://github.com/wmtorode/InnerSphereMap)  
**Original by:** Morphyum

---

## Features

- **4,700+ star systems** across three historical eras (see data below).
- All major factions represented on the map and in the Faction Screen.
- Adjusted jump distances scaled to the full Inner Sphere map size.
- Story mode removed (start directly in career mode).

---

## Data

Star system definitions live in `InnerSphereMap_data/`, organized by era:

| Directory | Era | Systems |
|---|---|---|
| `IS3025/` | 3025 (Succession Wars) | ~4,700 |
| `IS3040/` | 3040 (post-4th Succession War) | ~4,700 |
| `IS3063/` | 3063 (FedCom Civil War) | ~4,700 |

Each system is a `starsystemdef_*.json` file containing location, owner, tags, and shop data compatible with the BattleTech mod ecosystem.

The `DocsToSystemJSON/` tool converts source spreadsheet data into these JSON definitions.

---

## Installation

**Via ModTek (recommended):**

Place the `InnerSphereMap/` folder into your BattleTech mods directory:

```
# Steam
~/.steam/steam/steamapps/common/BATTLETECH/mods/

# Windows
C:\Users\<USERNAME>\AppData\LocalLow\Harebrained Schemes\BATTLETECH\mods\
```

Start a **new career** — existing saves are not compatible with a map change.

> The first load after installation takes longer than usual while ModTek processes the additional system definitions.

---

## Building the data tool

`DocsToSystemJSON/` is a standalone C# utility. It requires .NET and does not depend on the BattleTech game install:

```bash
dotnet build DocsToSystemJSON/
```

---

## Credits

- **Callyste** — faction icons
- **LegendKiller [CSV]** — vector icon sources
- **Jalif** — cinematic
- **mpstark** — BTML (original mod loader)
- **SaltyHotDog** — planet data gathering
- **Xavier** — NBT data
- **JamieWolf** — maintenance and fixes
