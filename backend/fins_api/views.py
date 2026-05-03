"""
DRF Views for Heat Sink Optimization API
"""

import os
import joblib
import pandas as pd
import numpy as np
from rest_framework import viewsets, status
import json
import traceback
from core.logger import get_api_logger
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    RecommendationRequestSerializer,
    RecommendationResponseSerializer,
    DesignSuggestionRequestSerializer,
    DesignSuggestionResponseSerializer,
    CFDOptimizationRequestSerializer,
    MLRequestSerializer,
    MLResponseSerializer,
    StatusResponseSerializer,
    MaterialListResponseSerializer,
)
from core.materials import list_materials, get_material_properties
from core.optimizer import DesignOptimizer
from core.cfd_closed_loop import (
    CFDOptimizationAgent,
    OptimizationConfig,
    ValidationCriteria,
    DesignIO,
)
from pathlib import Path
import tempfile


# Get base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_MODELS_DIR = os.path.join(BASE_DIR, 'ml_models')

# Load ML Models
logger = get_api_logger()

try:
    ml_model = joblib.load(os.path.join(ML_MODELS_DIR, "thermal_model.pkl"))
    inverse_model = joblib.load(os.path.join(ML_MODELS_DIR, "inverse_model.pkl"))
    logger.success("ML Models loaded into memory successfully")
except Exception as e:
    ml_model = None
    inverse_model = None
    logger.warning(f"ML Models not available", exception=e)


class HeatSinkViewSet(viewsets.ViewSet):
    """
    ViewSet for heat sink optimization endpoints.
    """

    @action(detail=False, methods=['get'], url_path='')
    def status(self, request):
        """
        Returns the API status.
        GET /
        """
        data = {
            "status": "System Operational",
            "message": "Heat Sink Optimization API"
        }
        serializer = StatusResponseSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def materials(self, request):
        """
        Returns list of available aluminum alloys.
        GET /materials
        """
        data = {"alloys": list_materials()}
        serializer = MaterialListResponseSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def recommend(self, request):
        """
        Generates an optimal heat sink design based on inputs.
        POST /recommend
        """
        # Validate input
        serializer = RecommendationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Extract validated data
            validated_data = serializer.validated_data
            motor_dict = validated_data['motor']
            env_dict = validated_data['environment']
            const_dict = validated_data['constraints']

            # Select Material to optimize for
            # If user prefers one, use it. Else, default to 6063-T5
            target_alloy = validated_data.get('preferred_alloy') or "6063-T5"

            # Initialize optimizer
            optimizer = DesignOptimizer(motor_dict, env_dict, const_dict)

            # Run optimization
            result = optimizer.optimize(material_name=target_alloy)

            if not result:
                return Response(
                    {
                        "detail": "No feasible design found for the given constraints. "
                                  "Try increasing Airflow or Casing Dimensions."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Add metadata
            result['alloy'] = target_alloy
            result['alloy_properties'] = get_material_properties(target_alloy)

            # Return response
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='suggest-design')
    def suggest_design(self, request):
        """
        Generates a shape-aware manufacturable heat sink proposal.
        POST /suggest-design
        """
        serializer = DesignSuggestionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validated_data = serializer.validated_data
            motor_dict = validated_data['motor']
            env_dict = validated_data['environment']
            const_dict = validated_data['constraints']
            candidate_limit = validated_data.get('candidate_limit', 3)
            target_alloy = validated_data.get('preferred_alloy') or "6063-T5"

            optimizer = DesignOptimizer(motor_dict, env_dict, const_dict)
            result = optimizer.suggest_design(
                material_name=target_alloy,
                limit=candidate_limit,
            )

            if not result:
                return Response(
                    {
                        "detail": "No feasible manufacturable design found for the given constraints. "
                                  "Try increasing airflow, height, or casing dimensions."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            response_serializer = DesignSuggestionResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='predict-ml')
    def predict_ml(self, request):
        """
        ML-based prediction endpoint.
        POST /predict-ml
        """
        if not inverse_model:
            return Response(
                {"detail": "ML Model not available."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Validate input
        serializer = MLRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validated_data = serializer.validated_data

            # Inverse Prediction: Predict Geometry from Problem
            # Features: ['Q_heat', 'Width', 'Length', 'Max_H']
            features = ['Q_heat', 'Width', 'Length', 'Max_H']
            data = [[
                validated_data['Q_heat'],
                validated_data['width'],
                validated_data['length'],
                validated_data['H']  # Use H as Max Height Constraint
            ]]
            df = pd.DataFrame(data, columns=features)

            # Predict
            pred = inverse_model.predict(df)[0]
            # Pred Schema: [Opt_N, Opt_H, Opt_t_base, Pred_Temp, Pred_Mass]

            N_pred = int(pred[0])
            H_pred = float(pred[1])
            t_base_pred = float(pred[2])

            # Calculate derived geometrical values for display
            width_m = validated_data['width']
            s_pred = (width_m - (N_pred * t_base_pred)) / (N_pred - 1) if N_pred > 1 else 0.0

            result = {
                "type": "Triangular",  # Optimal type from data
                "N": N_pred,
                "H": H_pred,
                "t_base": t_base_pred,
                "t_tip": 0.0,  # Triangular default
                "s": s_pred,
                "tb": 0.005,  # Fixed default
                "alloy": "6063-T5",
                "est_temp": pred[3],
                "est_mass": pred[4]
            }

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='cfd-optimize')
    def cfd_optimize(self, request):
        """
        AI-CFD closed-loop optimization endpoint.
        POST /cfd-optimize
        """
        # CFD optimization workflow removed. Accept only inlet_velocity and echo it back.
        serializer = CFDOptimizationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        inlet_velocity = serializer.validated_data.get('inlet_velocity')

        # Return a minimal response to keep API compatibility for frontends
        return Response(
            {
                "detail": "CFD optimization removed. Received inlet_velocity.",
                "inlet_velocity": inlet_velocity,
            },
            status=status.HTTP_200_OK,
        )


class StatusView(APIView):
    """
    Simple status view for root endpoint.
    """
    def get(self, request):
        """
        Returns the API status.
        GET /
        """
        data = {
            "status": "System Operational",
            "message": "Heat Sink Optimization API"
        }
        serializer = StatusResponseSerializer(data)
        return Response(serializer.data)


class MaterialsView(APIView):
    """
    Materials list view.
    """
    def get(self, request):
        """
        Returns list of available aluminum alloys.
        GET /materials
        """
        data = {"alloys": list_materials()}
        serializer = MaterialListResponseSerializer(data)
        return Response(serializer.data)


class HealthCheckView(APIView):
    """
    Lightweight health check endpoint for hosting platform probes.
    """
    def get(self, request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)
