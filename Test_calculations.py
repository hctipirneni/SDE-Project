import unittest
from pico_web_server import calculate_heat_index

class TestHeatIndexCalculation(unittest.TestCase):
    def test_heat_index_calculation(self):
        # Test with known temperature and humidity values
        temperature = 25  # Celsius
        humidity = 60     # Percentage
        expected_heat_index = calculate_heat_index(temperature, humidity)
        self.assertAlmostEqual(expected_heat_index, 25.3, places=1)  

        # Test with extreme values
        temperature = 40  # Celsius (extreme high)
        humidity = 10     # Percentage (extreme low)
        expected_heat_index = calculate_heat_index(temperature, humidity)
        self.assertAlmostEqual(expected_heat_index, 45.1, places=1)  

 for temp, hum, expected in test_cases:
            calculated_index = calculate_heat_index(temp, hum)
            self.assertAlmostEqual(calculated_index, expected, places=1)

if __name__ == '__main__':
    unittest.main()
    pass
