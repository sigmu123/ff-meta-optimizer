class AdvisorEngine:
    def __init__(self, loader):
        self.loader = loader

    def display_patch_summary(self):
        print(f"=== PATCH SUMMARY: {self.loader.patch_name.upper()} ===")
        
        # Categories list to parse
        categories = ["weapons_and_items", "characters", "modes_and_maps"]
        
        for cat in categories:
            print(f"\n--- Category: {cat.upper()} ---")
            
            if cat == "weapons_and_items":
                print("ITEMS & WEAPON ADJUSTMENTS DETECTED:")
                weapons_data = self.loader.weapons
                
                w_items = []
                if isinstance(weapons_data, dict):
                    w_items = weapons_data.get("base_attributes", weapons_data.get("weapon_adjustments", weapons_data.get("updates", [])))
                    if not w_items:
                        w_items = weapons_data
                elif isinstance(weapons_data, list):
                    w_items = weapons_data

                if isinstance(w_items, dict):
                    for w_name, w_info in w_items.items():
                        if isinstance(w_info, dict):
                            print(f" -> Weapon: {w_name} | Class: {w_info.get('category', 'N/A')}")
                elif isinstance(w_items, list):
                    for w in w_items:
                        if isinstance(w, dict):
                            w_name = w.get("weapon_name", w.get("name", w.get("id", "N/A")))
                            print(f" -> Weapon: {w_name} | Type/Change: {w.get('change_type', w.get('category', 'N/A'))}")

            elif cat == "characters":
                print("CHARACTER SKILL ADJUSTMENTS DETECTED:")
                
                sources = [self.loader.active_skills, self.loader.passive_skills, self.loader.characters]
                seen = set()
                
                for src in sources:
                    if not src:
                        continue
                    if isinstance(src, list):
                        for item in src:
                            if isinstance(item, dict):
                                c_name = item.get("character_id", item.get("character_name", item.get("name", ""))).upper()
                                s_name = item.get("skill_name", "N/A")
                                s_type = item.get("type", item.get("change_type", "Modified"))
                                if c_name and c_name not in seen:
                                    seen.add(c_name)
                                    print(f" -> Skill Adjust: {c_name} | Skill: {s_name} | Type: {s_type}")
                    elif isinstance(src, dict):
                        if "updates" in src and isinstance(src["updates"], list):
                            for item in src["updates"]:
                                c_name = item.get("character_name", item.get("name", "")).upper()
                                s_name = item.get("skill_name", "N/A")
                                if c_name and c_name not in seen:
                                    seen.add(c_name)
                                    print(f" -> Skill Adjust: {c_name} | Skill: {s_name}")
                        else:
                            for k, v in src.items():
                                if isinstance(v, dict):
                                    c_name = v.get("character_id", k).upper()
                                    s_name = v.get("skill_name", v.get("name", "N/A"))
                                    if c_name and c_name not in seen:
                                        seen.add(c_name)
                                        print(f" -> Skill Adjust: {c_name} | Skill: {s_name}")

            elif cat == "modes_and_maps":
                print("MAP & MODE MODIFICATIONS DETECTED:")
                utilities = getattr(self.loader, "modes_and_maps", getattr(self.loader, "utilities", None))
                print(f" -> Map & Utility Updates Loaded Successfully.")
