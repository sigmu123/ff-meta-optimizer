An execution-level breakdown of the system architecture, mathematical formulas, data structures, and pipeline flow for the **ff-meta-optimizer** repository based on the project files follows.

## 1. Directory & Architectural Topology

```text
sigmu123-ff-meta-optimizer/
├── README.md                          # Repository overview & project definition
├── LICENSE                            # MIT License (2026 sigmu123)
├── main.py                            # Primary execution entry point (Quick Execution Sheet UI)
├── advisor_engine.py                  # Standalone/isolated single-patch advisory runner
├── patch_loader.py                    # Multi-patch dynamic ingestion engine
├── .github/
│   └── workflows/
│       └── main.yml                   # CI/CD validation pipeline
├── core/
│   └── ttk_calculator.py              # Micro-variable damage & TTK/BTK equation engine
├── engine/
│   ├── combinatorial_tester.py        # Permutation matrix search space engine
│   └── damage_calculator.py           # Legacy damage calculation wrapper
├── interface/
│   └── prompt_parser.py               # Natural language intent & query parser
├── src/
│   ├── patch_ingestor.py              # Raw JSON validation & ingestion handlers
│   └── patch_router.py                # Active patch selection & version resolution
└── data/
    └── patches/                       # Granular patch history data store
        ├── patch_v1/                  # Legacy patch (BOOYAH Day)
        ├── patch_v2/                  # Legacy patch (New Age)
        ├── patch_5th_anniv/           # OB35 Patch
        ├── patch_rampage/             # OB34 Rampage Patch
        ├── patch_v33_heroes_arise/    # OB33 Patch
        ├── patch_ob52/                # OB52 Patch
        ├── patch_ob53/                # OB53 Patch
        └── patch_ob54/                # Current Active Meta Patch (Mid-2026)
```

## 2. Core Mathematical Engine (`core/ttk_calculator.py`)

The quantitative engine evaluates weapon lethality through three primary deterministic equations:

### I. Effective Damage Equation
Calculates damage per shot after applying range decay, armor penetration, and vest absorption:

$$\text{Effective Damage} = D_{\text{base}} \times (1 - \delta_{\text{range}}) \times \left[ 1 - \alpha_{\text{vest}} \times (1 - \pi_{\text{armor}}) \right]$$

* **$D_{\text{base}}$**: Base weapon damage attribute.
* **$\delta_{\text{range}}$**: Percentage loss due to distance decay ($0.0 \le \delta_{\text{range}} \le 1.0$).
* **$\alpha_{\text{vest}}$**: Base vest absorption percentage ($0.0 \le \alpha_{\text{vest}} \le 1.0$).
* **$\pi_{\text{armor}}$**: Weapon armor penetration percentage ($0.0 \le \pi_{\text{armor}} \le 1.0$).

### II. Bullets to Kill (BTK)
Determines the ceiling number of direct impacts required to deplete target health:

$$\text{BTK} = \left\lceil \frac{\text{HP}_{\text{target}}}{\text{Effective Damage}} \right\rceil$$

### III. Time to Kill (TTK)
Calculates exact engagement duration (in seconds) required for elimination:

$$\text{TTK} = (\text{BTK} - 1) \times R_{\text{fire}}$$

* **$R_{\text{fire}}$**: Rate of fire interval expressed in seconds per shot.

## 3. Data Schema Specifications

### Weapon Attributes Schema (`data/patches/patch_ob54/weapons/base_attributes.json`)

```json
{
  "patch_version": "OB54",
  "weapons": [
    {
      "weapon_id": "mp40",
      "name": "MP40",
      "category": "SMG",
      "status": "buffed",
      "rarity_tier": "Gold",
      "buffs": {
        "armor_penetration_boost_pct": 10.0,
        "accuracy_boost_pct": 5.0,
        "weapon_switch_speed_boost_pct": 25.0
      },
      "br_vending_machine_cost": 400
    }
  ]
}
```

### Character Skills Schema (`data/patches/patch_ob54/characters/active_skills.json`)

```json
{
  "patch_version": "OB54",
  "active_skills": [
    {
      "character_id": "chrono",
      "skill_name": "Time Turner",
      "type": "Defensive Shield",
      "status": "buffed",
      "shield_hp": 1000,
      "duration_seconds": 18.0,
      "cooldown_seconds": 45,
      "skill_boosts": [
        {
          "boost_id": "time_veil",
          "boost_name": "Time Veil",
          "one_way_vision_block": true
        }
      ]
    }
  ]
}
```

## 4. Pipeline Execution Flow

```text
[User Prompt / CLI Request]
         │
         ▼
┌─────────────────────────┐
│ interface/prompt_parser │ Parse execution mode, playstyle, and parameters
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│    src/patch_router     │ Resolve latest active patch version (e.g., "patch_ob54")
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│      patch_loader       │ Ingest character, weapon, and mechanic JSON definitions
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ core/ttk_calculator     │ Compute micro-variable Effective Damage, BTK, and TTK
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ engine/combinatorial    │ Run matrix search across Active × Passive × Loadout combinations
└──────────┬──────────────┘
           │
           ▼
[Formatted CLI Output / Quick Execution Sheet]
```

1. **Parser Initialization (`prompt_parser.py`)**: Converts raw queries (e.g., `"OB34 CS Ranked rush build"`) into structured scenario parameters (`mode`, `playstyle`).
2. **Patch Isolation & Routing (`patch_router.py`)**: Scans `data/patches/` and selects the latest isolated patch (defaulting to `OB54`).
3. **Dynamic Ingestion (`patch_loader.py`)**: Safely loads and normalizes nested JSON files across character abilities, weapon adjustments, and map tactics.
4. **Quantitative Evaluation (`ttk_calculator.py`)**: Performs micro-variable damage calculations across selected loadouts and weapon options.
5. **Permutation Matrix Search (`combinatorial_tester.py`)**: Evaluates permutations of 1 Active Skill + 3 Passive Skills + 1 Pet + Loadout + Weapons to identify optimal win-probability setups.
6. **Execution Output (`main.py` / `advisor_engine.py`)**: Outputs the calculated build metrics, weapon stats, and strategic guidance to the terminal.
