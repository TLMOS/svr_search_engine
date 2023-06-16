import os
import random

from locust import HttpUser, task, between


USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')


ADJECTIVES = [
    'red', 'green', 'blue', 'yellow', 'black', 'white', 'purple', 'orange',
    'pink', 'brown', 'tall', 'short', 'skinny', 'fat', 'big', 'small', 'tiny',
    'large', 'long', 'short', 'wide', 'narrow', 'thick', 'thin', 'heavy',
]
OBJECTS = [
    'cat', 'dog', 'man', 'woman', 'person', 'car', 'truck', 'bus',
    'bycicle', 'motorcycle', 'bag', 'backpack', 'suitcase', 'hat', 'cap',
    'helmet', 'shirt', 'pants', 'shoes', 'boots', 'glasses', 'sunglasses',
]
PROPOSITIONS = [
    'on', 'in', 'under', 'above', 'below', 'beside', 'behind', 'in front of',
    'with', 'without', 'for', 'against', 'over', 'under', 'between', 'among',
]


def generate_search_entry() -> str:
    """
    Generate random search entry.

    Returns:
    - entry (str): search entry
    """
    adjective = random.choice(ADJECTIVES)
    object_ = random.choice(OBJECTS)
    entry = f'{adjective} {object_}'
    for i in range(random.randint(0, 3)):
        preposition = random.choice(PROPOSITIONS)
        adjective = random.choice(ADJECTIVES)
        object_ = random.choice(OBJECTS)
        entry += f' {preposition} {adjective} {object_}'
    return entry


class QuickstartUser(HttpUser):
    wait_time = between(0.5, 1)

    def on_start(self):
        self.login()

    def on_stop(self):
        self.logout()

    def login(self):
        json = {"username": USERNAME, "password": PASSWORD}
        self.client.post("/login", json)

    def logout(self):
        self.client.post("/logout")

    @task(3)
    def search(self):
        params = {'search_entry': generate_search_entry()}
        self.client.get('/search', params=params, name='/search')

    @task(1)
    def index(self):
        self.client.get("/")

    @task(1)
    def profile(self):
        self.client.get("/profile")

    @task(1)
    def sources(self):
        self.client.get("/sources")
