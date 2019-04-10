from flask import Flask, render_template, request, jsonify
from latentSemanticIndexingService import LSI_Service
# Create the application instance
app = Flask(__name__)

LSI_SERVICE = LSI_Service()
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
    answer = LSI_SERVICE.getAnswer(query, format="HTML")
    return render_template('response.html', input=answer)
# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
