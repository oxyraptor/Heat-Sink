# Materials Database Documentation

**Reference Guide for Available Aluminum Alloys**

---

## Overview

The Fins API supports 6 aluminum alloys optimized for heat sink applications. Each material is characterized by thermal, mechanical, and manufacturing properties that affect design optimization.

---

## Material Specifications

### 1. Aluminum 6063-T5 (AL6063)

**Best For:** General-purpose heat sinks, balanced performance

```
ID:                    AL6063
Name:                  Aluminum 6063-T5
Density:               2.7 g/cm³
Thermal Conductivity:  201 W/m·K
Specific Heat:         896 J/kg·K
Cost:                  $2.50/kg
Machinability:         8/10 (Good)
Availability:          High
Applications:          Standard heat sinks, moderate power dissipation
Advantages:           - Excellent machinability
                      - Good thermal conductivity
                      - Cost-effective
                      - Easy surface finishing
Disadvantages:        - Not ideal for very high power
                      - Lower strength than 7075
```

---

### 2. Aluminum 6061-T6 (AL6061)

**Best For:** Structural applications requiring strength, aerospace

```
ID:                    AL6061
Name:                  Aluminum 6061-T6
Density:               2.7 g/cm³
Thermal Conductivity:  167 W/m·K
Specific Heat:         896 J/kg·K
Cost:                  $2.20/kg
Machinability:         7/10 (Good)
Availability:          High
Applications:          Structural heat sinks, lower thermal performance
Advantages:           - Good structural strength
                      - Fair machinability
                      - Corrosion resistant
                      - Good anodizing properties
Disadvantages:        - Lower thermal than 6063
                      - More difficult to machine
```

---

### 3. Aluminum 7075-T73 (AL7075)

**Best For:** High-power applications, extreme performance

```
ID:                    AL7075
Name:                  Aluminum 7075-T73
Density:               2.81 g/cm³
Thermal Conductivity:  130 W/m·K
Specific Heat:         960 J/kg·K
Cost:                  $12.00/kg
Machinability:         4/10 (Difficult)
Availability:          Medium
Applications:          Aerospace heat sinks, lightweight designs
Advantages:           - Highest strength-to-weight ratio
                      - Extreme durability
                      - Premium material
Disadvantages:        - Low thermal conductivity
                      - Very difficult to machine
                      - Very high cost
                      - Not ideal for pure thermal performance
```

---

### 4. Aluminum 2024-T4 (AL2024)

**Best For:** Industrial applications, strength-critical designs

```
ID:                    AL2024
Name:                  Aluminum 2024-T4
Density:               2.78 g/cm³
Thermal Conductivity:  121 W/m·K
Specific Heat:         875 J/kg·K
Cost:                  $5.50/kg
Machinability:         5/10 (Moderate)
Availability:          Medium-High
Applications:          Aircraft components, high-stress heat sinks
Advantages:           - High strength
                      - Moderate cost
                      - Good fatigue resistance
Disadvantages:        - Low thermal conductivity
                      - Poor corrosion resistance (needs coating)
                      - Difficult to machine
```

---

### 5. Aluminum 5083-H321 (AL5083)

**Best For:** Marine/corrosive environments, extreme conditions

```
ID:                    AL5083
Name:                  Aluminum 5083-H321
Density:               2.66 g/cm³
Thermal Conductivity:  120 W/m·K
Specific Heat:         900 J/kg·K
Cost:                  $3.80/kg
Machinability:         6/10 (Fair)
Availability:          High
Applications:          Marine heat sinks, corrosive environment protection
Advantages:           - Excellent corrosion resistance
                      - Seawater resistant
                      - Good formability
Disadvantages:        - Lower thermal conductivity
                      - Medium strength
```

---

### 6. Aluminum 1100-H14 (AL1100)

**Best For:** Cost-sensitive applications, decorative purposes

```
ID:                    AL1100
Name:                  Aluminum 1100-H14
Density:               2.71 g/cm³
Thermal Conductivity:  235 W/m·K
Specific Heat:         900 J/kg·K
Cost:                  $1.80/kg
Machinability:         9/10 (Excellent)
Availability:          Very High
Applications:          Budget heat sinks, prototype development
Advantages:           - Highest thermal conductivity
                      - Cheapest option
                      - Easiest to machine
                      - Excellent for prototyping
Disadvantages:        - Low strength
                      - Not suitable for high-stress applications
                      - Lower durability
```

---

## Thermal Properties Comparison

### Thermal Conductivity Ranking (Highest to Lowest)

1. **AL1100**: 235 W/m·K (Best thermal)
2. **AL6063**: 201 W/m·K
3. **AL6061**: 167 W/m·K
4. **AL2024**: 121 W/m·K
5. **AL5083**: 120 W/m·K
6. **AL7075**: 130 W/m·K

### Mechanical Strength Ranking (Highest to Lowest)

1. **AL7075**: Extreme (Yield ~505 MPa)
2. **AL2024**: Very High (Yield ~325 MPa)
3. **AL6061**: High (Yield ~275 MPa)
4. **AL5083**: Good (Yield ~215 MPa)
5. **AL6063**: Moderate (Yield ~170 MPa)
6. **AL1100**: Low (Yield ~110 MPa)

### Cost Ranking (Cheapest to Most Expensive)

1. **AL1100**: $1.80/kg
2. **AL6061**: $2.20/kg
3. **AL6063**: $2.50/kg
4. **AL5083**: $3.80/kg
5. **AL2024**: $5.50/kg
6. **AL7075**: $12.00/kg

### Machinability Ranking (Easiest to Hardest)

1. **AL1100**: 9/10 (Excellent)
2. **AL6063**: 8/10 (Good)
3. **AL6061**: 7/10 (Good)
4. **AL5083**: 6/10 (Fair)
5. **AL2024**: 5/10 (Moderate)
6. **AL7075**: 4/10 (Difficult)

---

## Selection Guide

### By Use Case

| Use Case                | Recommended      | Reason                                       |
| ----------------------- | ---------------- | -------------------------------------------- |
| **General-purpose**     | AL6063           | Best balance of thermal, cost, machinability |
| **Budget/Prototype**    | AL1100           | Cheapest, easiest to machine, good thermal   |
| **High-power**          | AL6063           | Best thermal conductivity in practical range |
| **Aerospace**           | AL7075           | Maximum strength, premium performance        |
| **Marine/Corrosion**    | AL5083           | Superior corrosion resistance                |
| **Cost-sensitive**      | AL1100           | Lowest material cost                         |
| **Structural strength** | AL7075 or AL2024 | Maximum durability                           |

### By Application

| Application | Material      | Thermal R | Cost      | Notes               |
| ----------- | ------------- | --------- | --------- | ------------------- |
| 1kW motor   | AL1100        | 0.12 K/W  | Low       | Best value          |
| 5kW motor   | AL6063        | 0.042 K/W | Medium    | Optimal choice      |
| 10kW motor  | AL6063/AL7075 | 0.020 K/W | High      | Consider hybrid     |
| Aerospace   | AL7075        | 0.050 K/W | Very High | Strength priority   |
| Marine      | AL5083        | 0.045 K/W | High      | Durability priority |
| Prototype   | AL1100        | 0.15 K/W  | Very Low  | Fast iteration      |

---

## Physical Properties Table

| Property               | AL1100    | AL6063  | AL6061  | AL7075  | AL2024  | AL5083    |
| ---------------------- | --------- | ------- | ------- | ------- | ------- | --------- |
| Density (g/cm³)        | 2.71      | 2.70    | 2.70    | 2.81    | 2.78    | 2.66      |
| Thermal Cond. (W/m·K)  | 235       | 201     | 167     | 130     | 121     | 120       |
| Specific Heat (J/kg·K) | 900       | 896     | 896     | 960     | 875     | 900       |
| Tensile Strength (MPa) | 90-110    | 170-230 | 240-310 | 500-570 | 325-435 | 215-290   |
| Yield Strength (MPa)   | 35-110    | 55-170  | 40-275  | 420-505 | 75-325  | 95-215    |
| Elastic Modulus (GPa)  | 69        | 69      | 69      | 72      | 73      | 70        |
| Corrosion Resistance   | Excellent | Good    | Fair    | Fair    | Poor\*  | Excellent |

\*AL2024 requires protective coating

---

## Thermal Performance Equations

When selecting materials, the thermal resistance calculation is:

$$R_{thermal} = \frac{\Delta T}{Q} = \frac{1}{h \cdot A_{effective} \cdot k_{material}}$$

Where:

- $\Delta T$ = Temperature difference (K)
- $Q$ = Heat dissipation (W)
- $h$ = Convection coefficient (W/m²·K)
- $A_{effective}$ = Effective heat transfer area (m²)
- $k_{material}$ = Material thermal conductivity (W/m·K)

### Example Calculation

For AL6063 with:

- Fin area: 0.15 m²
- Air velocity: 2 m/s (h ≈ 125 W/m²·K)
- Thermal conductivity: 201 W/m·K

$$R_{thermal} = \frac{1}{125 \times 0.15 \times 201} = 0.00266 \text{ K/W}$$

---

## API Usage

### Get All Materials

```bash
curl -X GET http://localhost:8001/api/materials/
```

### Use Material in Recommendation

```json
{
  "constraints": {
    "material": "AL6063"
  }
}
```

### Available Material IDs

- `AL1100` — General purpose, best thermal
- `AL6063` — Industry standard
- `AL6061` — Structural strength
- `AL7075` — Premium aerospace
- `AL2024` — Industrial high-strength
- `AL5083` — Marine environments

---

## Notes

1. **Prices** are approximate and may vary by supplier, quantity, and market conditions
2. **Availability** assumes standard suppliers; specialty alloys may require longer lead times
3. **Thermal conductivity** values are at 20°C; performance changes with temperature
4. **Machinability** ratings are relative; actual machining time depends on complexity
5. **Corrosion resistance** depends on surface treatment (anodizing, coating, etc.)

---

## References

- NACA Thermal Conductivity Tables
- ASM Handbook: Aluminum Alloys
- Alcoa Regional Technical Data Sheets

**Version:** 1.0.0  
**Last Updated:** 2026-03-25
