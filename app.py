from flask import Flask, request, jsonify
from geopy.geocoders import Nominatim
import openai
import config
import requests


openai.api_key = config.OPENAI_API_KEY
ipstack_api_key = config.IPSTACK_API_KEY
geolocator = Nominatim(user_agent='myGeocoder')  


# Continue with your Flask app code

app = Flask(__name__)

def generate_chat_response(user_input):
    # Call the OpenAI API to generate a response
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=user_input,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].text.strip()

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    user_ip_address = request.json['ipAddress']
    chat_gpt_request = construct_request(user_input, user_ip_address)
    response = generate_chat_response(chat_gpt_request)
    return jsonify({'message': response})

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

if __name__ == '__main__':
    app.run(port=8080, debug=True)
