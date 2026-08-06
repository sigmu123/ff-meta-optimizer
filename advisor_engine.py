        elif cat == "characters":
            print("CHARACTER SKILL ADJUSTMENTS DETECTED:")
            
            # Check List/Dict combinations across sources
            sources = [self.loader.active_skills, self.loader.passive_skills, self.loader.characters]
            seen = set()
            
            for src in sources:
                if not src:
                    continue
                # Agar data list ki shakal me ho (jaise OB33 active_skills list)
                if isinstance(src, list):
                    for item in src:
                        if isinstance(item, dict):
                            c_name = item.get("character_id", item.get("character_name", item.get("name", ""))).upper()
                            s_name = item.get("skill_name", "N/A")
                            s_type = item.get("type", item.get("change_type", "Modified"))
                            if c_name and c_name not in seen:
                                seen.add(c_name)
                                print(f" -> Skill Adjust: {c_name} | Skill: {s_name} | Type: {s_type}")
                # Agar data dictionary ki shakal me ho
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
