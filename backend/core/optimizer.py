
import numpy as np
from scipy.optimize import differential_evolution, root_scalar
from scipy.special import i0, i1
from core.materials import ALUMINUM_ALLOYS
import math
from abc import ABC, abstractmethod

# --- 1. Temperature-Dependent Air Properties ---
class AirProperties:
    @staticmethod
    def get_properties(T_kelvin):
        """
        Returns air properties at film temperature T (Kelvin).
        Correlations for dry air at 1 atm.
        """
        # Validity: 250K < T < 500K typically
        T = max(250, min(T_kelvin, 500)) 

        # Density (Ideal Gas Law approx)
        rho = 352.98 / T  # kg/m^3

        # Thermal Conductivity (k) - Sutherland's law approx or fit
        # k ~ 0.0263 @ 300K
        k = 1.5207e-11 * T**3 - 4.8574e-8 * T**2 + 1.0184e-4 * T - 3.9333e-4 # W/(m·K) polynomial fit

        # Dynamic Viscosity (mu)
        mu = 1.458e-6 * (T**1.5) / (T + 110.4) # Sutherland

        # Specific Heat (Cp)
        # Cp is mostly constant ~1005 for this range, but small variation:
        cp = 1.005e3 # J/(kg·K)

        # Kinematic Viscosity (nu)
        nu = mu / rho

        # Prandtl Number (Pr)
        pr = (cp * mu) / k
        
        # Volumetric expansion coefficient (beta) = 1/T for ideal gas
        beta = 1.0 / T

        return {
            'rho': rho, 'k': k, 'mu': mu, 'cp': cp,
            'nu': nu, 'pr': pr, 'beta': beta
        }

# --- 2. Geometric Hierarchy ---
class FinGeometry(ABC):
    def __init__(self, N, H, t_base, length, width):
        self.N = int(N)
        self.H = H
        self.t_base = t_base
        self.L = length # Flow length
        self.W = width # Heat sink width (across fins)

        # Spacing calculation
        # W_total = N*t_base + (N-1)*s
        if self.N > 1:
            self.s = (self.W - self.N * self.t_base) / (self.N - 1)
        else:
            self.s = 0.0 
            
    def is_valid(self):
        # Physical constraints
        if self.s < 0.0005: return False # Min 0.5mm
        if self.t_base < 0.0005: return False
        if self.H < 0.01: return False
        return True

    @abstractmethod
    def fin_efficiency(self, h_conv, k_mat):
        pass

    @abstractmethod
    def surface_area(self):
        pass
        
    @abstractmethod
    def volume(self):
        pass
    
    @abstractmethod
    def get_details(self):
        pass

class RectangularFin(FinGeometry):
    def fin_efficiency(self, h, k):
        # Adiabatic tip
        m = math.sqrt((2 * h) / (k * self.t_base))
        Lc = self.H + (self.t_base / 2.0)
        mLc = m * Lc
        if mLc == 0: return 1.0
        return math.tanh(mLc) / mLc

    def surface_area(self):
        # Area contributing to convection: 2*H*L + t*L (tip)
        return self.N * (2 * self.H * self.L + self.t_base * self.L)

    def volume(self):
        return self.N * (self.H * self.t_base * self.L)

    def get_details(self):
        return {'type': 'Rectangular', 't_tip': self.t_base, 'taper_angle': 0.0}

class TriangularFin(FinGeometry):
    def fin_efficiency(self, h, k):
        # Explicit Bessel: eta = (1/mL) * I1(2mL)/I0(2mL)
        m = math.sqrt((2 * h) / (k * self.t_base))
        val = m * self.H
        if val < 1e-6: return 1.0 
        num = i1(2 * val)
        den = i0(2 * val)
        if den == 0: return 0.0
        return (1.0 / val) * (num / den)

    def surface_area(self):
        slant = math.sqrt(self.H**2 + (self.t_base/2.0)**2)
        return self.N * (2 * slant * self.L) 

    def volume(self):
        return self.N * (0.5 * self.H * self.t_base * self.L)

    def get_details(self):
        angle = math.degrees(math.atan((self.t_base / 2.0) / self.H)) if self.H > 0 else 0
        return {'type': 'Triangular', 't_tip': 0.0, 'taper_angle': angle}

class TrapezoidalFin(FinGeometry):
    def __init__(self, N, H, t_base, length, width):
        super().__init__(N, H, t_base, length, width)
        self.t_tip = 0.5 * t_base # Fixed ratio

    def fin_efficiency(self, h, k):
        # Approximation using mean thickness
        t_mean = (self.t_base + self.t_tip) / 2.0
        m = math.sqrt((2 * h) / (k * t_mean))
        Lc = self.H + (self.t_tip / 2.0)
        mLc = m * Lc
        if mLc == 0: return 1.0
        return math.tanh(mLc) / mLc

    def surface_area(self):
        slant = math.sqrt(self.H**2 + ((self.t_base - self.t_tip)/2.0)**2)
        return self.N * (2 * slant * self.L + self.t_tip * self.L)

    def volume(self):
        area = 0.5 * (self.t_base + self.t_tip) * self.H
        return self.N * (area * self.L)
        
    def get_details(self):
        angle = math.degrees(math.atan(((self.t_base - self.t_tip)/ 2.0) / self.H)) if self.H > 0 else 0
        return {'type': 'Trapezoidal', 't_tip': self.t_tip, 'taper_angle': angle}


# --- 3. Advanced Thermal Model (Physics Engine) ---
class AdvancedThermalModel:
    def __init__(self, motor_specs, environment):
        self.motor = motor_specs
        self.env = environment
        
        self.motor_diameter = motor_specs.get('motor_diameter', 0.1)  # Motor diameter
        self.motor_length = motor_specs.get('motor_length', 0.1)      # Motor length
        self.W = motor_specs.get('casing_width', 0.1)                 # Heat sink width
        self.L = motor_specs.get('casing_length', 0.1)                # Heat sink length
        
        self.epsilon = 0.8 # Anodized Aluminum
        self.sigma = 5.67e-8 

    def get_heat_load(self):
        eff = self.motor.get('efficiency')
        p_rated = self.motor.get('rated_power', 1000.0)
        
        if eff:
            return max(0, (p_rated / eff) - p_rated)
        
        v = self.motor.get('rated_voltage')
        i = self.motor.get('rated_current')
        if v and i:
            return max(0, (v * i) - p_rated)
            
        return (p_rated / 0.85) - p_rated

    def solve_equilibrium(self, fin_geom: FinGeometry, mat_k, t_base_plate):
        Q_total = self.get_heat_load()
        if Q_total <= 0: return {'T_surface': self.env.get('ambient_temp', 25.0), 'R_total': 0, 'h_avg': 0, 'rad_pct': 0, 'valid': True}

        T_amb = self.env.get('ambient_temp', 25.0)
        airflow = self.env.get('airflow_type', 'Natural')
        vel = self.env.get('air_velocity', 0.0)
        g = 9.81
        
        R_cond_base = t_base_plate / (mat_k * self.W * self.L)
        
        # Iterative Solver State
        self.last_h = 0
        self.last_rad_q = 0
        
        def heat_balance_residual(T_s):
            if T_s <= T_amb: return -Q_total 
            
            T_film = (T_s + T_amb) / 2.0
            props = AirProperties.get_properties(T_film + 273.15)
            
            s = fin_geom.s
            if s <= 1e-4: return -Q_total 
            
            dT = T_s - T_amb
            
            # Convection h calculation
            h_conv = 1.0
            
            if airflow == 'Natural':
                # Elenbaas Correlation for Parallel Plates
                Ra_s = (g * props['beta'] * dT * (s**4)) / (props['nu'] * (props['k'] / (props['rho']*props['cp'])) * self.L)
                if Ra_s > 0:
                    Nu_s = (Ra_s / 24.0) * (1.0 - math.exp(-35.0 / Ra_s))**0.75
                    h_conv = (Nu_s * props['k']) / s
            else: 
                # Teertstra et al. (1998)
                Re_L = (vel * self.L) / props['nu']
                # Nu_plate -> simplified Sieder-Tate/Flat Plate
                if Re_L < 5e5:
                    Nu_L = 0.664 * (Re_L**0.5) * (props['pr']**(1.0/3.0))
                else:
                    Nu_L = 0.037 * (Re_L**0.8) * (props['pr']**(1.0/3.0))
                h_conv = (Nu_L * props['k']) / self.L
            
            self.last_h = h_conv
            
            # Radiation
            # Estimate A_rad as envelope area
            A_rad = self.W * self.L + 2 * fin_geom.H * self.L + 2 * self.W * fin_geom.H
            Q_rad = self.sigma * self.epsilon * A_rad * ((T_s + 273.15)**4 - (T_amb + 273.15)**4)
            self.last_rad_q = Q_rad
            
            # Fin Efficiency & Total Q
            eta_f = fin_geom.fin_efficiency(h_conv, mat_k)
            A_exposed_base = (fin_geom.N - 1) * fin_geom.s * self.L
            A_fin_total = fin_geom.surface_area() 
            
            # Effective Area
            A_eff = A_exposed_base + (A_fin_total * eta_f)
            Q_conv = h_conv * A_eff * dT
            
            return (Q_conv + Q_rad) - Q_total

        try:
            sol = root_scalar(heat_balance_residual, bracket=[T_amb+0.1, T_amb+500], method='brentq')
            T_surf = sol.root
        except:
             T_surf = T_amb + 999 

        R_total = (T_surf - T_amb) / Q_total
        rad_pct = (self.last_rad_q / Q_total) * 100 if Q_total > 0 else 0
        
        return {
            'T_surface': T_surf,
            'R_total': R_total + R_cond_base, 
            'h_avg': self.last_h,
            'rad_pct': rad_pct,
            'valid': fin_geom.is_valid()
        }


# --- 4. Optimization Engine ---
class DesignOptimizer:
    def __init__(self, motor_specs, environment, constraints):
        self.motor = motor_specs
        self.env = environment
        self.constraints = constraints
        self.model = AdvancedThermalModel(motor_specs, environment)
        self.target_alloy = "6063-T5" 

    def create_geometry(self, x, geom_type):
        N, H, t_base, tb = x
        L = self.motor.get('casing_length', 0.1)
        W = self.motor.get('casing_width', 0.1)
        
        if geom_type == 'Rectangular':
            return RectangularFin(N, H, t_base, L, W)
        elif geom_type == 'Triangular':
            return TriangularFin(N, H, t_base, L, W)
        elif geom_type == 'Trapezoidal':
            return TrapezoidalFin(N, H, t_base, L, W)
        return None

    def evaluate_full(self, x, geom_type, mat_name=None):
        if mat_name is None: mat_name = self.target_alloy
        
        mat = ALUMINUM_ALLOYS.get(mat_name, ALUMINUM_ALLOYS["6063-T5"])
        geom = self.create_geometry(x, geom_type)
        
        if not geom.is_valid():
            return {'valid': False, 'mass': 1e6, 'temperature': 1e6}
            
        sim_res = self.model.solve_equilibrium(geom, mat['thermal_conductivity'], x[3])
        
        vol_base = geom.W * geom.L * x[3]
        vol_fins = geom.volume()
        mass = (vol_base + vol_fins) * mat['density']
        
        return {
            'valid': sim_res['valid'],
            'temperature': sim_res['T_surface'],
            'thermal_resistance': sim_res['R_total'],
            'mass': mass,
            'geometry': geom_type,
            'h_avg': sim_res['h_avg'],
            'rad_pct': sim_res['rad_pct'],
            'parameters': {
                'N': geom.N, 'H': geom.H, 't_base': geom.t_base, 'tb': x[3], 's': geom.s,
                **geom.get_details()
            },
            'alloy': mat_name
        }

    def objective_function(self, x, geom_type):
        res = self.evaluate_full(x, geom_type)
        if not res['valid']: return 1e6
        
        max_temp = self.motor.get('max_temp', 100.0)
        max_h = self.constraints.get('max_height', 0.1)
        min_t = self.constraints.get('min_fin_thickness', 0.001)
        
        if x[1] > max_h: return 1e6
        if x[2] < min_t: return 1e6
        
        T = res['temperature']
        M = res['mass']
        
        penalty = 0
        if T > max_temp:
            penalty = (T - max_temp)**2 * 100 
            
        return M * 10.0 + penalty

    def calculate_sensitivity(self, x, geom_type):
        base_res = self.evaluate_full(x, geom_type)
        T_base = base_res['temperature']
        grads = {}
        
        # Perturb N (+1)
        x_N = np.array(x, dtype=float).copy()
        x_N[0] += 1
        res_N = self.evaluate_full(x_N, geom_type)
        grads['N'] = (res_N['temperature'] - T_base)
        
        # Perturb others (1%)
        names = ['N', 'H', 't_base', 'tb']
        for i in range(1, 4):
            x_new = np.array(x, dtype=float).copy()
            x_new[i] *= 1.01
            res_new = self.evaluate_full(x_new, geom_type)
            dVal = x[i] * 0.01
            if dVal > 0:
                grads[names[i]] = (res_new['temperature'] - T_base) / dVal
            else:
                grads[names[i]] = 0
        return grads


    def optimize(self, material_name="6063-T5", geometry_type=None):
        self.target_alloy = material_name
        if geometry_type:
            geometries = [geometry_type]
        else:
            geometries = ['Rectangular', 'Triangular', 'Trapezoidal']
        
        best = None
        candidates = []  # Store all valid candidates for comparison
        
        max_h = self.constraints.get('max_height', 0.1)
        min_t = self.constraints.get('min_fin_thickness', 0.001)
        t_max = self.motor.get('max_temp', 100.0)
        
        bounds = [
            (5, 60),       # N
            (0.01, max_h), # H
            (min_t, 0.01), # t_base
            (0.002, 0.015) # tb
        ]
        
        for geom in geometries:
            res = differential_evolution(
                self.objective_function,
                bounds,
                args=(geom,),
                strategy='best1bin',
                maxiter=30,
                popsize=10,
                tol=0.01,
                seed=42
            )
            
            # Evaluate final result with INTEGER N
            x_final = res.x
            x_final[0] = round(x_final[0])
            final_eval = self.evaluate_full(x_final, geom, material_name)
            
            if not final_eval['valid']:
                continue
            
            t_actual = final_eval['temperature']
            
            # Only consider designs that meet temperature constraint
            if t_actual <= t_max:
                # Store candidate with metric for ranking
                # Primary metric: Thermal Resistance (lower is better)
                # Secondary metric: Mass (lower is better)
                r_thermal = final_eval['thermal_resistance']
                mass = final_eval['mass']
                
                candidates.append({
                    'design': final_eval,
                    'thermal_resistance': r_thermal,
                    'mass': mass,
                    'temperature': t_actual,
                    'geometry': geom,
                    'score': r_thermal  # Primary sorting metric
                })
        
        # If no designs meet temperature constraint, pick the closest one
        if not candidates:
            best_temp_margin = float('inf')
            for geom in geometries:
                res = differential_evolution(
                    self.objective_function,
                    bounds,
                    args=(geom,),
                    strategy='best1bin',
                    maxiter=30,
                    popsize=10,
                    tol=0.01,
                    seed=42
                )
                x_final = res.x
                x_final[0] = round(x_final[0])
                final_eval = self.evaluate_full(x_final, geom, material_name)
                if final_eval['valid']:
                    temp_excess = final_eval['temperature'] - t_max
                    if temp_excess < best_temp_margin:
                        best_temp_margin = temp_excess
                        best = final_eval
        else:
            # Sort by thermal resistance (best thermal performance first)
            candidates.sort(key=lambda c: c['score'])
            best = candidates[0]['design']
        
        if best:
            x_opt = [best['parameters']['N'], best['parameters']['H'], best['parameters']['t_base'], best['parameters']['tb']]
            grads = self.calculate_sensitivity(x_opt, best['geometry'])
            best['sensitivity'] = {k: f"{v:.2f}" for k,v in grads.items()}
            
            # Dominant factor
            norm_imp = {k: abs(float(v)) for k,v in best['sensitivity'].items()}
            best['dominant_factor'] = max(norm_imp, key=norm_imp.get) if norm_imp else "None"
            
        return best
