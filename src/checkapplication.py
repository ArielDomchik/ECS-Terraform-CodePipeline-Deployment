import unittest
from server import app, getcountry, getweather

class TestWeather(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get('http://0.0.0.0/')
        self.assertEqual(response.status_code, 200)

    def test_error(self):
        response = self.app.get('http://0.0.0.0/error')
        self.assertEqual(response.status_code, 200)

    def test_weather(self):
        response = self.app.post('/weather', data={'city': 'Cairo'})
        self.assertEqual(response.status_code, 200)

    def test_weather2(self):
        response = self.app.post('/weather', data={'city': ' '})
        self.assertNotEqual(response.status_code, 200)

    def test_getcountry(self):
        self.assertEqual(getcountry('Cairo'), 'Egypt')

    def test_getweather(self):
        lat = 29.96265
        lon = 31.25044
        forecast = getweather(lat, lon)
        self.assertEqual(len(forecast), 14)
"""
@pytest.fixture
def client():
    client = start_client()
    client.config.update({'TESTING': True})
    yield client

@pytest.fixture
def app(client):
    return app.test_client()

def test_index(app):
    response = app.get('/')
    assert response.status_code == 200

def test_error(app):
    response = app.get('/error')
    assert response.status_code == 200

def test_weather(app):
    response = app.post('/weather', data={'city': 'Cairo'})
    assert response.status_code == 200

def test_weather2(app):
    response = app.post('/weather', data={'city': ' '})
    assert response.status_code != 200

def test_getcountry():
    assert getcountry('Cairo') == 'Egypt'

def test_getweather():
    lat = 29.96265
    lon = 31.25044
    forecast = getweather(lat, lon)
    assert len(forecast) == 14
"""

if __name__ == '__main__':
    unittest.main()
