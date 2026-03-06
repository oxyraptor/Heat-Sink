"""
DRF Serializers for Heat Sink Optimization API
"""

from rest_framework import serializers


class MotorSpecsSerializer(serializers.Serializer):
    """Serializer for motor specifications"""
    motor_type = serializers.CharField(default="Servo")
    rated_power = serializers.FloatField(required=True, help_text="Power in Watts")
    rated_voltage = serializers.FloatField(required=True, help_text="Voltage in Volts")
    rated_current = serializers.FloatField(required=False, allow_null=True, help_text="Current in Amps")
    efficiency = serializers.FloatField(required=False, allow_null=True, help_text="Efficiency (0.0 to 1.0)")
    max_temp = serializers.FloatField(required=True, help_text="Maximum temperature in Celsius")
    motor_diameter = serializers.FloatField(required=True, help_text="Motor diameter in meters")
    motor_length = serializers.FloatField(required=True, help_text="Motor length in meters")
    casing_width = serializers.FloatField(required=False, default=0.1, help_text="Casing width in meters")
    casing_length = serializers.FloatField(required=False, default=0.1, help_text="Casing length in meters")
    casing_height = serializers.FloatField(required=False, default=0.1, allow_null=True, help_text="Casing height in meters")


class EnvironmentSpecsSerializer(serializers.Serializer):
    """Serializer for environment specifications"""
    ambient_temp = serializers.FloatField(default=25.0, help_text="Ambient temperature in Celsius")
    airflow_type = serializers.ChoiceField(
        choices=['Forced', 'Natural', 'Mixed'],
        default='Forced',
        help_text="Type of airflow"
    )
    air_velocity = serializers.FloatField(default=5.0, help_text="Air velocity in m/s")


class ConstraintSpecsSerializer(serializers.Serializer):
    """Serializer for design constraints"""
    max_height = serializers.FloatField(default=0.1, help_text="Maximum height in meters (default 100mm)")
    min_fin_thickness = serializers.FloatField(default=0.001, help_text="Minimum fin thickness in meters")
    max_weight = serializers.FloatField(required=False, allow_null=True, help_text="Maximum weight in kg")


class RecommendationRequestSerializer(serializers.Serializer):
    """Serializer for heat sink recommendation request"""
    motor = MotorSpecsSerializer(required=True)
    environment = EnvironmentSpecsSerializer(required=True)
    constraints = ConstraintSpecsSerializer(required=True)
    preferred_alloy = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class MLRequestSerializer(serializers.Serializer):
    """Serializer for ML prediction request"""
    Q_heat = serializers.FloatField(required=True)
    width = serializers.FloatField(required=True)
    length = serializers.FloatField(required=True)
    ambient = serializers.FloatField(required=True)
    velocity = serializers.FloatField(required=True)
    N = serializers.IntegerField(required=True)
    H = serializers.FloatField(required=True)
    t_base = serializers.FloatField(required=True)
    geom_type = serializers.ChoiceField(
        choices=['Rectangular', 'Triangular'],
        required=True,
        help_text="Geometry type"
    )


class MaterialPropertiesSerializer(serializers.Serializer):
    """Serializer for material properties"""
    thermal_conductivity = serializers.FloatField()
    density = serializers.FloatField()
    cost_per_kg = serializers.FloatField()


class RecommendationResponseSerializer(serializers.Serializer):
    """Serializer for heat sink recommendation response"""
    type = serializers.CharField()
    N = serializers.IntegerField()
    H = serializers.FloatField()
    t_base = serializers.FloatField()
    t_tip = serializers.FloatField()
    s = serializers.FloatField()
    tb = serializers.FloatField()
    alloy = serializers.CharField()
    alloy_properties = MaterialPropertiesSerializer()
    temperature = serializers.FloatField()
    thermal_resistance = serializers.FloatField()
    mass = serializers.FloatField()
    cost = serializers.FloatField()
    h_avg = serializers.FloatField()
    is_valid = serializers.BooleanField()
    sensitivity = serializers.DictField()


class MLResponseSerializer(serializers.Serializer):
    """Serializer for ML prediction response"""
    type = serializers.CharField()
    N = serializers.IntegerField()
    H = serializers.FloatField()
    t_base = serializers.FloatField()
    t_tip = serializers.FloatField()
    s = serializers.FloatField()
    tb = serializers.FloatField()
    alloy = serializers.CharField()
    est_temp = serializers.FloatField()
    est_mass = serializers.FloatField()


class StatusResponseSerializer(serializers.Serializer):
    """Serializer for status endpoint"""
    status = serializers.CharField()
    message = serializers.CharField()


class MaterialListResponseSerializer(serializers.Serializer):
    """Serializer for materials list endpoint"""
    alloys = serializers.ListField(child=serializers.CharField())
