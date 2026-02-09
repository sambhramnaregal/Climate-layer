import unittest
from app import app

class WeatherAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_load(self):
        """Test if the home page loads successfully."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Atmosphere', response.data)

    def test_api_weather_valid(self):
        """Test API with valid coordinates (London)."""
        # Note: This actually calls the external API. In a real CI/CD, we would mock it.
        # But for this verification, we want to ensure the API key works.
        response = self.app.get('/api/weather?lat=51.52&lon=-0.11')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('location', data)
        self.assertIn('current', data)
        self.assertEqual(data['location']['name'], 'London')

    def test_api_missing_params(self):
        """Test API with missing parameters."""
        response = self.app.get('/api/weather')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
