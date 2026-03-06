# Machine Learning & Optimization Algorithms

This document details the algorithmic core of the Heat Sink Recommendation System. While the physics engine handles the _simulation_, the **Optimization Engine** uses evolutionary strategies (a subset of AI/ML) to find the best design.

---

## 1. Differential Evolution (Global Optimization)

The system uses **Differential Evolution (DE)**, a stochastic population-based optimization algorithm. It is chosen for its robustness in navigating non-linear, non-differentiable landscapes (like thermal fluid dynamics).

### Core Concept

DE evolves a population of candidate designs (genomes) over generations.

- **Genome**: Vector $X = [N, H, t_{base}, t_{base\_plate}]$
- **Population**: $P = \{X_1, X_2, ..., X_{NP}\}$ (e.g., 20 candidates).

### Steps per Generation

For each candidate (Target Vector) $X_i$:

1.  **Mutation**:
    Three random distinct vectors $X_{r1}, X_{r2}, X_{r3}$ are chosen.
    A **Donor Vector** $V$ is created:
    $$ V = X*{r1} + F \cdot (X*{r2} - X\_{r3}) $$
    - $F$ (Mutation Factor) controls the exploration scale.

2.  **Crossover**:
    A **Trial Vector** $U$ is formed by mixing the Target $X_i$ and Donor $V$:
    - For each parameter $j$:
      $$ U*j = \begin{cases} V_j & \text{if } rand() \le CR \\ X*{i,j} & \text{otherwise} \end{cases} $$
    - $CR$ (Crossover Probability) controls diversity.

3.  **Selection**:
    The Trial Vector $U$ is evaluated:
    $$ Score*{trial} = ObjectiveFunction(U) $$
    $$ Score*{target} = ObjectiveFunction(X_i) $$

    If $Score_{trial} < Score_{target}$, the Trial Vector $U$ replaces $X_i$ in the next generation.
    $$ X\_{i, next} = U $$

---

## 2. Objective Function (Loss Function)

The algorithm minimizes a composite **Loss Function** that balances Mass and Feasibility.

### Formula

$$ L(X) = (Mass \times w*{mass}) + Penalty(T*{surf}) $$

### Components

1.  **Mass Cost**:
    - Calculated mass of the heat sink (Alloy Density $\times$ Volume).
    - Weight $w_{mass} = 10$. This drives the optimizer toward lighter (cheaper) designs.

2.  **Temperature Penalty (Soft Constraint)**:
    - Ensures the design meets the cooling requirement ($T_{surf} < T_{max}$).
    - If $T_{surf} > T_{max}$:
      $$ Penalty = (T*{surf} - T*{max})^2 \times 100 $$
    - The Quadratic term creates a steep gradient pushing the optimizer back to the valid region.
    - If valid, Penalty = 0.

---

## 3. Sensitivity Analysis (Gradient Approximation)

Once the optimal design $X^*$ is found, the system performs a local sensitivity analysis to explain _why_ it works and what factors matter.

### Method: Finite Difference

Since we don't have analytical gradients for the complex Nu correlations, we approximate them numerically.

For each parameter $p \in \{N, H, t, ...\}$:

1.  Perturb parameter by $\delta$ (1%): $p' = p \times 1.01$
2.  Re-evaluate Temperature: $T' = Model(p')$
3.  Calculate Gradient:
    $$ \frac{\partial T}{\partial p} \approx \frac{T' - T\_{optimal}}{p \times 0.01} $$

### Interpretation

- **Magnitude**: A large absolute value means the temperature is very sensitive to this parameter.
- **Sign**:
  - Negative (-): Increasing parameter reduces temp (Good). Example: Fin Height.
  - Positive (+): Increasing parameter increases temp (Bad).
- **Dominant Factor**: The parameter with the highest normalized sensitivity magnitude.

---

## 4. Root Finding (Iterative Solver)

Used within the Physics Engine (called by the Optimizer).

- **Algorithm**: Brent's Method (`brentq`).
- **Goal**: Find $T_s$ such that $Residual(T_s) = 0$.
- **Convergence**: Guaranteed for the monotonic heat balance function in the range $[T_{amb}, T_{amb} + 500]$.
