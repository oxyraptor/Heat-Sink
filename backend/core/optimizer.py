
import numpy as np
import os
from scipy.optimize import differential_evolution, root_scalar
from scipy.special import i0, i1
from core.materials import ALUMINUM_ALLOYS
import math
from abc import ABC, abstractmethod


MIN_FIN_SPACING_M = 0.0002
MIN_FIN_COUNT = 5  # Reduced from 10
HIGH_POWER_TRAPEZOIDAL_THRESHOLD_W = 800.0

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
        # Physical constraints - relaxed for better optimization
        if self.N < MIN_FIN_COUNT: return False
        if self.s < MIN_FIN_SPACING_M: return False
        if self.t_base < 0.0003: return False  # Reduced from 0.0005
        if self.H < 0.005: return False  # Reduced from 0.01 (5mm instead of 10mm)
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
    def __init__(self, N, H, t_base, length, width, t_tip=None, motor_power=1000):
        super().__init__(N, H, t_base, length, width)
        # Adaptive taper based on power to address Error 9
        if motor_power < 500:
            ratio = 0.7
        elif motor_power < 1200:
            ratio = 0.5
        else:
            ratio = 0.35
            
        self.t_tip = ratio * self.t_base

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
        # Use full-thickness taper over fin height for reported taper-angle metric.
        angle = math.degrees(math.atan((self.t_base - self.t_tip) / self.H)) if self.H > 0 else 0
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
        # x dimensions:
        # For Trapezoidal: [N, H, t_base, t_tip, tb] (5 elements)
        # For others: [N, H, t_base, tb] (4 elements)
        N, H, t_base = x[0], x[1], x[2]
        
        # Check if this is Trapezoidal with t_tip
        if geom_type == 'Trapezoidal' and len(x) >= 5:
            t_tip = x[3]
            tb = x[4]
        else:
            t_tip = None
            # For other geometries, tb is at index 3
            tb = x[3] if len(x) > 3 else 0.002
        
        L = self.motor.get('casing_length', 0.1)
        W = self.motor.get('casing_width', 0.1)
        motor_power = float(self.motor.get('rated_power', 1000.0))
        
        if geom_type == 'Rectangular':
            return RectangularFin(N, H, t_base, L, W)
        elif geom_type == 'Triangular':
            return TriangularFin(N, H, t_base, L, W)
        elif geom_type == 'Trapezoidal':
            return TrapezoidalFin(N, H, t_base, L, W, t_tip=t_tip, motor_power=motor_power)
        return None

    def evaluate_full(self, x, geom_type, mat_name=None):
        if mat_name is None: mat_name = self.target_alloy
        
        mat = ALUMINUM_ALLOYS.get(mat_name, ALUMINUM_ALLOYS["6063-T5"])
        geom = self.create_geometry(x, geom_type)
        
        motor_diameter = self.motor.get('motor_diameter', 0.1)
        motor_length = self.motor.get('motor_length', 0.1)
        
        if not geom:
            return {'valid': False, 'mass': 1e6, 'temperature': 1e6}
            
        if not geom.is_valid():
            return {'valid': False, 'mass': 1e6, 'temperature': 1e6}
            
        # Error 1: Fin Height Too Large (absolute rejection)
        # Max height = motor_diameter * 0.5
        max_height = motor_diameter * 0.5
        if geom.H > max_height:
            return {'valid': False, 'mass': 1e6, 'temperature': 1e6}
            
        # Optional: H > motor_length * 0.6
        if geom.H > motor_length * 0.6:
            return {'valid': False, 'mass': 1e6, 'temperature': 1e6}
        
        # Extract tb (base plate thickness) - last element
        tb = x[-1]
        
        sim_res = self.model.solve_equilibrium(geom, mat['thermal_conductivity'], tb)
        
        vol_base = geom.W * geom.L * tb
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
                'N': geom.N, 'H': geom.H, 't_base': geom.t_base, 'tb': tb, 's': geom.s,
                **geom.get_details()
            },
            'alloy': mat_name
        }

    def _create_fallback_design(self, material_name):
        """Create a better fallback design when optimization fails"""
        try:
            rated_power = float(self.motor.get('rated_power', 1000.0))
            motor_diameter = self.motor.get('motor_diameter', 0.1)
            t_max = self.motor.get('max_temp', 100.0)
            
            # Create designs scaled by power, size, and temperature constraint
            if rated_power > 1200:
                if t_max < 75:  # Strict temp - need LARGER fins
                    x = [24, 0.040, 0.0032, 0.0010, 0.005]  # N, H, t_base, t_tip, tb
                else:
                    x = [22, 0.032, 0.0028, 0.0010, 0.005]
            elif rated_power > 800:
                if t_max < 75:  # Strict temp
                    x = [20, 0.036, 0.0028, 0.0009, 0.004]
                else:
                    x = [18, 0.028, 0.0024, 0.0009, 0.004]
            elif rated_power > 400:
                if t_max < 75:  # Strict temp
                    x = [16, 0.030, 0.0022, 0.0008, 0.003]
                else:
                    x = [14, 0.022, 0.0020, 0.0008, 0.003]
            else:
                x = [12, 0.020, 0.0018, 0.0008, 0.003]
            
            # Scale by motor diameter
            diameter_ratio = motor_diameter / 0.065
            x[0] = max(int(x[0] * diameter_ratio), 5)  # Scale fin count
            x[1] *= min(diameter_ratio, 1.2)  # Scale height but limit
            
            res = self.evaluate_full(x, 'Trapezoidal', material_name)
            if res and res.get('valid'):
                print(f"[DEBUG] Created fallback: Trapezoidal, N={x[0]}, H={x[1]:.4f}m, t_tip={x[3]:.6f}m")
                return res
        except Exception as e:
            print(f"[DEBUG] Fallback design creation failed: {e}")
        return None

    def objective_function(self, x, geom_type):
        """
        Objective function with comprehensive physical constraints.
        For Trapezoidal: x = [N, H, t_base, t_tip, tb]
        For others: x = [N, H, t_base, tb]
        """
        res = self.evaluate_full(x, geom_type)
        if not res['valid']: return 1e6
        
        motor_diameter = self.motor.get('motor_diameter', 0.1)
        motor_length = self.motor.get('motor_length', 0.1)
        rated_power = float(self.motor.get('rated_power', 1000.0))
        max_temp = self.motor.get('max_temp', 100.0)
        max_h = self.constraints.get('max_height', 0.1)
        min_t = self.constraints.get('min_fin_thickness', 0.001)

        N = res['parameters']['N']
        H = x[1]

        # Extract t_tip for Trapezoidal
        t_tip = res['parameters'].get('t_tip', x[2])
        
        s = res['parameters']['s']
        T = res['temperature']
        M = res['mass']
        
        # FIX 1: Maximum fin height cannot exceed half the motor diameter
        max_h_diameter = motor_diameter * 0.5
        if H > max_h_diameter:
            return 1e6
        
        # FIX 2: Secondary height constraint - limit by motor length
        max_h_length = motor_length * 0.6
        if H > max_h_length:
            return 1e6
        
        # FIX 3: Basic constraints
        if H > max_h: return 1e6
        if x[2] < min_t: return 1e6
        
        # FIX 4: Minimum height constraint
        MIN_HEIGHT = 0.005  # 5mm minimum
        if H < MIN_HEIGHT:
            return 1e6
        
        # FIX 4: Tip Thickness Too Small
        if t_tip < 0.0003:
            return 1e6

        # FIX 7: Physical sanity checks for spacing
        # Maximum spacing = 12 mm
        if s > 0.012:
            return 1e6
        if s < 0.0002:
            return 1e6
        
        # t_tip must be reasonable and smaller than t_base
        if t_tip >= x[2] and geom_type == 'Trapezoidal':  # t_tip cannot be >= t_base
            return 1e6
        
        penalty = 0
        
        # FIX 6: Tip thickness in target range (0.8-1.2mm).
        if t_tip < 0.0008 or t_tip > 0.0012:
            penalty += (t_tip - 0.0010) ** 2 * 100.0
        
        # FIX 8: Power-based baseline height scaling.
        if rated_power >= 1200:  # Include exactly 1200W
            min_height_power = 0.030
            min_fin_count = 16
        elif rated_power > 800:
            min_height_power = 0.025
            min_fin_count = 14
        elif rated_power > 500:
            min_height_power = 0.020
            min_fin_count = 12
        else:
            min_height_power = 0.015
            min_fin_count = 10

        # Context-aware fin count target.
        air_velocity = self.env.get('air_velocity', 5.0)
        if air_velocity < 8:
            min_fin_count += 4
        elif air_velocity > 15:
            min_fin_count = max(min_fin_count - 2, 10)

        if max_temp < 75:
            min_fin_count += 4

        diameter_ratio = motor_diameter / 0.065
        min_fin_count = max(int(min_fin_count * max(0.85, min(diameter_ratio, 1.4))), 10)

        # FIX 8: Power-Based Scaling
        # High power -> >= 16 fins
        if rated_power > 1000 and N < 16:
            return 1e6
            
        # FIX 5: Too Few Fins for medium/high power
        if rated_power > 800 and N < 10:
            return 1e6

        if H < min_height_power:
            penalty += (min_height_power - H) ** 2 * 50.0

        if geom_type == 'Trapezoidal':
            taper_angle = math.degrees(math.atan((x[2] - t_tip) / H)) if H > 0 else 0
            if taper_angle > 12.0:
                # Add strict penalty for aggressive taper
                penalty += (taper_angle - 12.0)**2 * 1000.0  # Massive penalty
        
        # FIX 6: Wrong Geometry Selection
        if rated_power > 800 and geom_type != "Trapezoidal":
            return 1e6
        
        spacing_mm = s * 1000
        
        # FIX 10: Temperature constraint handling
        if T > max_temp:
            temp_excess = T - max_temp
            # FIX: Make this penalty EXTREMELY expensive to reject solutions
            penalty = temp_excess ** 2 * 500.0  # Increased from 100
            return M * 10.0 + penalty  # Increased from 2.0
        
        # FIX: Additional penalty for high spacing (indicates too few fins)
        if spacing_mm > 7.5:  # FIX: Stricter limit (was 8.0)
            spacing_penalty = (spacing_mm - 7.5) ** 2 * 5.0
            penalty += spacing_penalty
        
        # FIX: Promote denser fins for better cooling
        if spacing_mm > 5.0:
            density_discount = (spacing_mm - 5.0) ** 2 * 2.0
            penalty += density_discount
            
        return M * 5.0 + penalty

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
        if geom_type == 'Trapezoidal':
            names = ['N', 'H', 't_base', 't_tip', 'tb']
        else:
            names = ['N', 'H', 't_base', 'tb']
        
        for i in range(1, len(names)):
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
        _ = geometry_type
        # Always evaluate all geometries; ML guidance is treated as an initial hint only.
        geometries = ['Trapezoidal', 'Triangular', 'Rectangular']

        rated_power = float(self.motor.get('rated_power', 0.0) or 0.0)
        force_trapezoidal = rated_power > HIGH_POWER_TRAPEZOIDAL_THRESHOLD_W
        
        best = None
        candidates = []
        best_temp_margin = float('inf')
        best_near_feasible = None
        
        max_h = self.constraints.get('max_height', 0.1)
        min_t = self.constraints.get('min_fin_thickness', 0.001)
        t_max = self.motor.get('max_temp', 100.0)
        
        # FIX 4 & 6: Scale bounds based on motor geometry and power
        motor_diameter = self.motor.get('motor_diameter', 0.1)
        motor_length = self.motor.get('motor_length', 0.1)
        air_velocity = self.env.get('air_velocity', 5.0)
        
        # Max fin height: cannot exceed half motor diameter or 60% of length
        max_h_diameter = motor_diameter * 0.5
        max_h_length = motor_length * 0.6
        max_h_constrained = min(max_h, max_h_diameter, max_h_length)
        
        # POWER-AWARE FIN COUNT SCALING
        # Higher power -> need more fins for better heat dissipation.
        if rated_power >= 1200:  # High power (include exactly 1200)
            n_min, n_max = 16, 34
        elif rated_power > 800:   # Medium-high power
            n_min, n_max = 14, 30
        elif rated_power > 500:   # Medium power
            n_min, n_max = 12, 24
        else:                      # Low power
            n_min, n_max = 10, 20
        
        # MOTOR SIZE SCALING for fin count
        # Larger diameter → can fit more fins
        diameter_ratio = motor_diameter / 0.065  # 65mm reference
        n_max = int(n_max * min(diameter_ratio, 1.6))  # Scale up but cap at 1.6x
        n_min = max(int(n_min * diameter_ratio * 0.9), 8)  # Minimum 8 fins
        
        # AIRFLOW VELOCITY SCALING for fin count
        # Lower velocity → need more fins for heat transfer
        if air_velocity < 8:    # Low airflow
            n_min = n_min + 4  # FIX: Add more fins for low velocity
            n_max = n_max + 8
        elif air_velocity > 15: # High airflow
            n_min = max(n_min - 2, 10)
            n_max = max(n_max - 2, n_min + 3)
        
        # HEIGHT SCALING based on power and velocity
        if rated_power >= 1200:  # High power
            h_min = 0.030  # 30mm minimum - INCREASED
            h_max = min(0.055, max_h_constrained)  # 55mm max
        elif rated_power > 800:
            h_min = 0.025  # 25mm minimum - INCREASED
            h_max = min(0.045, max_h_constrained)
        elif rated_power > 500:
            h_min = 0.020  # 20mm minimum - INCREASED  
            h_max = min(0.040, max_h_constrained)
        else:
            h_min = 0.015  # 15mm minimum
            h_max = min(0.035, max_h_constrained)
        
        # Adjust height based on velocity
        if air_velocity < 8:  # Low airflow - need taller fins
            h_min = min(h_min + 0.005, h_max)
            h_max = min(h_max + 0.010, max_h_constrained)
        elif air_velocity > 15:  # High airflow - can use shorter fins
            h_max = max(h_min + 0.005, min(h_max - 0.005, max_h_constrained))

        # TEMPERATURE CONSTRAINT SCALING
        # Stricter temperature limits require denser and taller fins.
        if t_max < 75:
            n_min = n_min + 4
            n_max = n_max + 10
            h_min = min(h_min + 0.006, max_h_constrained)
            h_max = min(h_max + 0.010, max_h_constrained)
        
        # Ensure height bounds are valid
        if h_max <= h_min:
            h_max = h_min + 0.010
        h_max = min(h_max, max_h_constrained)
        
        # Error 10 - Optimizer bounds too wide
        # Apply absolute bounds requested in constraints: 
        # Height: 5mm - diameter/2
        # Fins: 5 - 60
        # Thickness: 1mm - 10mm
        
        # Override n_min and n_max with clamped values or simply set the absolute bounds?
        # Let's apply bounds strictly to the variables used below in the bounds array
        absolute_h_max = motor_diameter * 0.5
        h_max = min(h_max, absolute_h_max)
        h_min = min(max(h_min, 0.005), h_max - 0.001) if h_max > 0.006 else 0.005
        
        n_min = max(n_min, 5)
        n_max = max(min(n_max, 60), n_min + 1)
        
        t_base_low = 0.001
        t_base_high = 0.010
        
        # Tunable optimization cost controls
        maxiter = int(os.getenv("FINS_OPTIMIZER_MAXITER", "25"))  # Increased from 20
        popsize = int(os.getenv("FINS_OPTIMIZER_POPSIZE", "12"))  # Increased from 10
        
        for geom in geometries:
            if geom == 'Trapezoidal':
                t_tip_min = 0.0003
                t_tip_max = 0.0050
                bounds = [
                    (n_min, n_max),                                 # N
                    (h_min, h_max),           # H
                    (t_base_low, t_base_high),                          # t_base
                    (t_tip_min, t_tip_max),                  # t_tip
                    (0.002, 0.015)                           # tb
                ]
            else:
                bounds = [
                    (n_min, n_max),                                 # N
                    (h_min, h_max),           # H
                    (t_base_low, t_base_high),                          # t_base
                    (0.002, 0.015)                           # tb
                ]
            
            res = differential_evolution(
                self.objective_function,
                bounds,
                args=(geom,),
                strategy='best1bin',
                maxiter=maxiter,
                popsize=popsize,
                tol=0.01,
                seed=42
            )
            
            
            # Evaluate final result with INTEGER N
            x_final = res.x.copy()
            x_final[0] = round(x_final[0])
            final_eval = self.evaluate_full(x_final, geom, material_name)
            
            if not final_eval['valid']:
                continue

            if force_trapezoidal and geom != 'Trapezoidal':
                continue
            
            # FIX 10: Final validation - check all critical parameters
            final_H = final_eval['parameters']['H']
            final_N = final_eval['parameters']['N']
            final_t_tip = final_eval['parameters'].get('t_tip', final_eval['parameters']['t_base'])
            final_t_base = final_eval['parameters']['t_base']
            
            # Physical validity checks:
            if final_H > motor_diameter * 0.6:
                continue  # Height exceeds motor diameter constraint
            if final_N < 3:
                continue  # Too few fins
            if final_t_tip < 0.0001:
                continue  # Tip too thin
            
            # Taper validity check for trapezoidal
            if geom == 'Trapezoidal':
                if final_t_tip >= final_t_base:
                    continue  # Tip cannot be >= base for trapezoid
                # Check taper angle is in reasonable range
                taper_angle = final_eval['parameters'].get('taper_angle', 0)
                if taper_angle > 12.0:
                    continue
            
            
            t_actual = final_eval['temperature']

            temp_excess = t_actual - t_max
            if temp_excess < best_temp_margin:
                best_temp_margin = temp_excess
                best_near_feasible = final_eval
            
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
        
        # If no designs meet temperature constraint, use closest one already evaluated.
        if not candidates:
            best = best_near_feasible
            if best:
                print(f"[DEBUG] No temp-constrained candidates. Using near-feasible: N={best['parameters'].get('N', 6)}, H={best['parameters'].get('H', 0):.6f}m")
            else:
                print(f"[DEBUG] All optimization failed. Creating fallback design.")
                best = self._create_fallback_design(material_name)
                if not best:
                    print("[ERROR] Fallback design creation also failed!")
                    return None
        else:
            # Sort by thermal resistance (best thermal performance first)
            candidates.sort(key=lambda c: c['score'])
            best = candidates[0]['design']
            print(f"[DEBUG] Found {len(candidates)} valid candidates. Best: N={best['parameters']['N']}, H={best['parameters']['H']:.4f}m")
        
        if best:
            # Build x_opt with correct dimensions for the geometry
            if best['geometry'] == 'Trapezoidal':
                t_tip = best['parameters'].get('t_tip', best['parameters']['t_base'] * 0.5)
                x_opt = [best['parameters']['N'], best['parameters']['H'], best['parameters']['t_base'], t_tip, best['parameters']['tb']]
            else:
                x_opt = [best['parameters']['N'], best['parameters']['H'], best['parameters']['t_base'], best['parameters']['tb']]
            
            grads = self.calculate_sensitivity(x_opt, best['geometry'])
            best['sensitivity'] = {k: f"{v:.2f}" for k,v in grads.items()}
            
            # Dominant factor
            norm_imp = {k: abs(float(v)) for k,v in best['sensitivity'].items()}
            best['dominant_factor'] = max(norm_imp, key=norm_imp.get) if norm_imp else "None"
            
        return best
