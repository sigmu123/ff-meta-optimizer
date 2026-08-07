================================================
FILE: engine/damage_calculator.py
================================================
from core.ttk_calculator import MechanicsEngine

class DamageCalculatorWrapper:
    """
    Legacy wrapper maintaining interface backward compatibility with core MechanicsEngine.
    """
    @staticmethod
    def calculate_damage(base_dmg: float, range_decay: float = 0.0, vest_absorb: float = 0.0, armor_pen: float = 0.0) -> float:
        return MechanicsEngine.calculate_effective_damage(base_dmg, range_decay, vest_absorb, armor_pen)
