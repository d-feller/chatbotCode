from flask import Flask, render_template, request
from Chatbot import Chatbot

# Create the application instance
app = Flask(__name__)

chatty = Chatbot()
# Create a URL route in our application for "/"
@app.route('/api/chatbot/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/api/chatbot

    :return:        the rendered template 'home.html'
    """
    return render_template('home.html')

@app.route('/api/chatbot/ask')
def query():
    """
    This function takes the client's query and
    sends back a response
    """
    query = request.args.get('question')

    answer = chatty.getAnswer(query)
    print("ANSWER: ", answer.html)
    return render_template('response.html', input=answer.html)
# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
