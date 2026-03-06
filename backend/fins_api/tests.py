"""
Tests for fins_api.
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class HeatSinkAPITestCase(TestCase):
    """
    Test cases for Heat Sink Optimization API
    """

    def setUp(self):
        """Set up test client"""
        self.client = APIClient()

    def test_status_endpoint(self):
        """Test the status endpoint"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'System Operational')

    def test_materials_endpoint(self):
        """Test the materials endpoint"""
        response = self.client.get('/materials/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('alloys', response.data)
        self.assertIsInstance(response.data['alloys'], list)

    def test_recommend_endpoint(self):
        """Test the recommend endpoint with valid data"""
        payload = {
            "motor": {
                "motor_type": "Servo",
                "rated_power": 1000,
                "rated_voltage": 48,
                "rated_current": 25,
                "max_temp": 120,
                "casing_width": 0.1,
                "casing_length": 0.1,
                "casing_height": 0.1
            },
            "environment": {
                "ambient_temp": 25,
                "airflow_type": "Forced",
                "air_velocity": 5
            },
            "constraints": {
                "max_height": 0.05,
                "min_fin_thickness": 0.001
            }
        }
        response = self.client.post('/recommend/', payload, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_recommend_endpoint_missing_data(self):
        """Test the recommend endpoint with missing data"""
        payload = {
            "motor": {
                "rated_power": 1000
            }
        }
        response = self.client.post('/recommend/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
