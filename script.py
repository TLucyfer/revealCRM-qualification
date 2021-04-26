from config import SERVICES
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import logging, requests


app = Flask(__name__)

# logging configuration
# logging.basicConfig(filename=Config.LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
app.logger.info('Successfully configured logs')

# function #
def get_text(website):
    try:
        page = requests.get(website)
    except Exception as e:
        print(Exception("An error has occured with website request", str(e)))
        return ""
    try:
        soup = BeautifulSoup(page.content, 'html.parser')
    except Exception as e:
        print(Exception("An error has occured with html.parser", str(e)))
        return ""
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    text = text.lower()
    return text

def qualification(website):
    res = []
    text = get_text(website)
    for service in SERVICES:
        if service in text:
            res.append(service)
    return res
                
# endpoint #
@app.route('/qualification', methods=['GET'])
def qualification_route():
    """
    Qualifie un prospect
    ---
    parameters:
      - name: mail
        in: POST
        type: string
        required: true
    responses:
      200:
        description: Le script s'est bien lancé et terminé
      422:
        description: Erreur de format 
      400:
        description: Exception declenché 
      500:
        description: Erreur server ou une exception non anticipée
    """
    try:
      jdata = request.get_json()
      website = jdata.get('website')
      result = qualification(website)
      indice = len(result)
      return jsonify(list=result, indice=indice)
    except Exception as e:
      return jsonify(type=str(type(e)), message=str(e)), 500


if __name__ == "__main__":
    app.run()    