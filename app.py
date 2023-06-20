from flask import Flask, request, jsonify, g
from geopy.geocoders import Nominatim
import openai
import config
import requests


openai.api_key = config.OPENAI_API_KEY
ipstack_api_key = config.IPSTACK_API_KEY
geolocator = Nominatim(user_agent='myGeocoder')  

app = Flask(__name__)

class SingletonMap:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.map = {}

        return cls._instance

    def add_item(self, key, value):
        self.map[key] = value

    def get_item(self, key, default=None):
        return self.map.get(key, default)

def generate_chat_response(user_input):
    # Call the OpenAI API to generate a response
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=user_input,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].text.strip()

@app.route('/')
def index():
    singleton_map = SingletonMap()

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    user_ip_address = request.json['ipAddress']
    chat_gpt_request = construct_request(user_input, user_ip_address)
    record_query(chat_gpt_request)
    response = generate_chat_response(chat_gpt_request)
    return jsonify({'response': response})

@app.route('/stats', methods=['GET'])
def get_stats():
    singleton_map = SingletonMap()
    return jsonify(dict(singleton_map.map.items()))

def get_lat_long_from_ip(ip_address):

    url = f'http://api.ipstack.com/{ip_address}?access_key={ipstack_api_key}'

    response = requests.get(url)
    data = response.json()

    latitude = data['latitude']
    longitude = data['longitude']

    return latitude, longitude

def get_address_from_lat_long(latitude, longitude):
    location = geolocator.reverse((latitude, longitude))
    address = location.address
    return address

def construct_request(message, ip_address):
    if ip_address and ip_address.strip():
        latitude, longitude = get_lat_long_from_ip(ip_address)
        address = get_address_from_lat_long(latitude, longitude)
        return f'{message} near {address}'
    else:
        return message

def record_query(query):
    singleton_map = SingletonMap()
    print(query)
    if singleton_map.get_item(query) == 1:
        singleton_map.add_item(query, singleton_map.get_item(query) + 1)
    else:
        singleton_map.add_item(query, 1)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
