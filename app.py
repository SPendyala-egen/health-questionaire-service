from flask import Flask, request, jsonify
import openai
import config

openai.api_key = config.OPENAI_API_KEY

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
    response = generate_chat_response(user_input)
    return jsonify({'message': response})


if __name__ == '__main__':
    app.run(port=8080, debug=True)
