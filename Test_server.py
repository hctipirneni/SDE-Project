import unittest
import requests
import threading

class TestServerResponses(unittest.TestCase):
    def setUp(self):
        # Start the server in a separate thread
        self.server_thread = threading.Thread(target=start_server_function)
        self.server_thread.start()
        # Wait for the server to start (adjust time as needed)
        time.sleep(2)

    def tearDown(self):
        stop_server_function()  # Implement this function to stop the server gracefully
        self.server_thread.join()  # Wait for the server thread to finish

    def test_root_path(self):
        response = requests.get('http://10.0.0.40:8051/')  # Replace 'your_server_ip' with the actual IP
        self.assertEqual(response.status_code, 200)
       

    def test_sensor_data_path(self):
        response = requests.get('http://10.0.0.40:8051/sensor_data')
        self.assertEqual(response.status_code, 200)
        

  

if __name__ == '__main__':
    unittest.main()
