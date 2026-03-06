
"""
Aluminum Alloy Database for Heat Sink Applications.
Contains thermal, mechanical, and cost properties.
"""

ALUMINUM_ALLOYS = {
    "6063-T5": {
        "thermal_conductivity": 200,  # W/m·K
        "density": 2700,             # kg/m^3
        "yield_strength": 145,       # MPa
        "cost_factor": 1.0,          # Baseline cost
        "manufacturability": 1.0,    # Excellent extrusion
        "description": "Standard architectural alloy, excellent extrudability, good thermal conductivity."
    },
    "6061-T6": {
        "thermal_conductivity": 167,
        "density": 2700,
        "yield_strength": 276,
        "cost_factor": 1.1,
        "manufacturability": 0.9,
        "description": "Structural alloy, higher strength, slightly lower conductivity."
    },
    "1050-H14": {
        "thermal_conductivity": 222,
        "density": 2705,
        "yield_strength": 85,
        "cost_factor": 1.05,
        "manufacturability": 0.8,
        "description": "Electrically conductive, high thermal conductivity, low strength."
    },
    "3003-H14": {
        "thermal_conductivity": 159,
        "density": 2730,
        "yield_strength": 145,
        "cost_factor": 1.0,
        "manufacturability": 0.95,
        "description": "Good corrosion resistance, moderate strength."
    },
    "5052-H32": {
        "thermal_conductivity": 138,
        "density": 2680,
        "yield_strength": 193,
        "cost_factor": 1.2,
        "manufacturability": 0.85,
        "description": "High fatigue strength, excellent corrosion resistance (marine)."
    }
}

def get_material_properties(alloy_name: str):
    """Retrieves properties for a specific alloy."""
    return ALUMINUM_ALLOYS.get(alloy_name)

def list_materials():
    """Lists all available alloys."""
    return list(ALUMINUM_ALLOYS.keys())
