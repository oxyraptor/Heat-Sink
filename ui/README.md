# UI Documentation

This UI is the front-end layer for the Heat Sink Optimization System and is designed to support an AI-driven engineering workflow.

## AI-CFD Closed-Loop Workflow

### Process

1. AI tool generates an initial design (geometry + parameters).
2. The generated output is passed to CFD for physics simulation.
3. CFD results are validated against performance constraints.
4. Decision:
   - Accept when requirements are met.
   - Redesign loop when constraints fail.

### Validation Criteria Examples

- Drag below threshold
- Pressure drop acceptable
- Flow uniformity within tolerance
- Temperature within limit

### Loop Diagram

```text
AI generates design
		  ↓
CFD simulates physics
		  ↓
Check performance
	↓           ↓
 Accept      Improve
					 ↓
				 AI redesign
					 ↓
				 repeat
```

## Technical Interpretation

- AI = design generator / optimizer
- CFD = physics truth engine
- Validator = objective function + constraints
- Loop = closed-loop optimization

This maps to:

- AI + simulation optimization
- Surrogate-based design
- Generative engineering
- Autonomous engineering loop

## Local Development

```bash
npm install
npm run dev
```

## Current UI Features

- `Heat Sink Optimizer` tab for existing recommendation workflow
- `CFD Optimization` tab for closed-loop CFD runs via `POST /cfd-optimize/`
- `Unified Optimizer` tab with a left vertical configuration panel and right results panel
- Turbulence separation toggle (`Allow Turbulence Separation`) in Unified Optimizer
- Analysis Results card in Unified Optimizer with:
  - Valid Design
  - Geometry
  - Parameters (Number of Fins, Fin Height, Fin Spacing, Geometry Type, Tip Thickness, Taper Angle)
  - Material Alloy
- Iteration-level CFD result rendering (status, metrics, changes)

Primary UI components:

- `src/components/UnifiedOptimization.tsx`
- `src/components/CFDOptimization.tsx`
- Integrated from `src/App.tsx`

Default dev server: `http://localhost:5173/`
