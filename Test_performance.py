from locust import HttpUser, task, between

class SensorUser(HttpUser):
    wait_time = between(1, 3)  # Time between requests (randomized between 1 and 3 seconds)

    @task
    def get_root(self):
        self.client.get("/")

    @task
    def get_sensor_data(self):
        self.client.get("/sensor_data")

   
# Command to run the test with Locust: locust -f test_performance.py
