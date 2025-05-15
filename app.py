#import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import openai
from secrets import API_KEY_OAI
#from config import Config
from openai import OpenAI

app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username=username,
    password=password,
    hostname="mknomics.mysql.pythonanywhere-services.com",
    databasename=databasename,
)

#app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app) # Initialize Database Connection to bls


# OpenAI client setup
client = OpenAI(api_key = API_KEY_OAI)
openai.api_key = API_KEY_OAI

# Model and Messages Setup
class TextEntry(db.Model):
    __tablename__ = 'TextEntries'
    id = db.Column(db.Integer, primary_key=True)
    text_value = db.Column(db.Text)

class FedReport(db.Model):
    __tablename__ = 'FedReport'
    id = db.Column(db.Integer, primary_key=True)
    text_value = db.Column(db.Text)

class Abi(db.Model):
    __tablename__ = 'Abi'
    id = db.Column(db.Integer, primary_key=True)
    text_value = db.Column(db.Text)

@app.route('/')
def index():
    first_entry = db.session.query(TextEntry).order_by(TextEntry.id.desc()).first()  # This retrieves the first row

    if first_entry:
        bls_raw = first_entry.text_value  # Access the 'text_value' column
    else:
        bls_raw = "No data available."
    return render_template('index.html', bls_raw=bls_raw)

@app.route('/generate', methods=['POST'])
def generate_response():
    # BLS Data
    first_entry_bls = db.session.query(TextEntry).order_by(TextEntry.id.desc()).first()  # This retrieves the first row
    bls_raw = first_entry_bls.text_value  # Access the 'text_value' column

    # FED Data
    first_entry_fed = db.session.query(FedReport).order_by(FedReport.id.desc()).first()  # This retrieves the first row
    fed_raw = first_entry_fed.text_value  # Access the 'text_value' column

    # Abi Data
    first_entry_abi = db.session.query(Abi).order_by(Abi.id.desc()).first()  # This retrieves the first row
    abi_raw = first_entry_abi.text_value  # Access the 'text_value' column

    raw = bls_raw + fed_raw + abi_raw
    system_message = request.json.get('system_message')

    # Define the message structure
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": raw}
    ]

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Extract the content
    res_content = response.choices[0].message.content

    return jsonify({"content": res_content})

@app.route('/combined', methods=['POST'])
def combined():
    # BLS Data
    first_entry_bls = db.session.query(TextEntry).order_by(TextEntry.id.desc()).first()  # This retrieves the first row
    bls_raw = first_entry_bls.text_value  # Access the 'text_value' column

    # FED Data
    first_entry_fed = db.session.query(FedReport).order_by(FedReport.id.desc()).first()  # This retrieves the first row
    fed_raw = first_entry_fed.text_value  # Access the 'text_value' column

    # Abi Data
    first_entry_abi = db.session.query(Abi).order_by(Abi.id.desc()).first()  # This retrieves the first row
    abi_raw = first_entry_abi.text_value  # Access the 'text_value' column

    raw = bls_raw + fed_raw + abi_raw
    system_message = "How will these market conditions impact the demand for chainlink fence this quarter?"
    # Define the message structure for OpenAI API
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": raw}
    ]

    # Call OpenAI API to generate the response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Extract the content from the OpenAI response
    res_content = response.choices[0].message.content

    return jsonify({"content": res_content})



@app.route('/fed_sentiment', methods=['POST'])
def fed_sentiment():
    # Ensure we use db_fredpress for mknomics$fredpress database
    first_entry_fredpress = db.session.query(FedReport).order_by(FedReport.id.desc()).first()

    if first_entry_fredpress:
        fredpress_raw = first_entry_fredpress.text_value  # Access the 'text_value' column
    else:
        fredpress_raw = "No data available."

    system_message = "summarize the report in 150 words"

    # Define the message structure for OpenAI API
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": fredpress_raw}
    ]

    # Call OpenAI API to generate the response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Extract the content from the OpenAI response
    res_content = response.choices[0].message.content

    return jsonify({"content": res_content})




@app.route('/abi', methods=['POST'])
def abi_sentiment():

    first_entry_abi = db.session.query(Abi).order_by(Abi.id.desc()).first()

    if first_entry_abi:
        abi_raw = first_entry_abi.text_value  # Access the 'text_value' column
    else:
        abi_raw = "No data available."

    system_message = "summarize the report in 150 words"

    # Define the message structure for OpenAI API
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": abi_raw}
    ]

    # Call OpenAI API to generate the response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Extract the content from the OpenAI response
    res_content = response.choices[0].message.content

    return jsonify({"content": res_content})





@app.route('/sentiment', methods = ['POST'])
def sentiment():
    first_entry = db.session.query(TextEntry).order_by(TextEntry.id.desc()).first()  # This retrieves the first row

    if first_entry:
        bls_raw = first_entry.text_value  # Access the 'text_value' column
    else:
        bls_raw = "No data available."


    system_message = "summarize the sentiment of how good or bad the labor market is based on this report.  Limit the response to 150 words"
    #bls_raw = request.json.get('bls_raw')

    # Define the message structure
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": bls_raw}
    ]

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Extract the content
    res_content = response.choices[0].message.content

    return jsonify({"content": res_content})


@app.route('/numerical_rating', methods = ['POST'])
def numerical_rating():
    first_entry = db.session.query(TextEntry).order_by(TextEntry.id.desc()).first()  # This retrieves the first row

    if first_entry:
        bls_raw = first_entry.text_value  # Access the 'text_value' column
    else:
        bls_raw = "No data available."

    system_message = "summarize the outlook of this job report in one number ranging from 0 to 10 with 0 being a bad labor market and 10 being excellent. Give reasoning"
    # Define the message structure
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": bls_raw}
    ]

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Extract the content
    res_content = response.choices[0].message.content

    return jsonify({"content": res_content})


@app.route('/clickable_query', methods=['POST'])
def clickable_query():
    # Trigger the predefined question about employment outlook
    first_entry = db.session.query(TextEntry).order_by(TextEntry.id.desc()).first()  # This retrieves the first row

    if first_entry:
        bls_raw = first_entry.text_value  # Access the 'text_value' column
    else:
        bls_raw = "No data available."

    system_message = request.json.get('system_message')

    # Define the message structure
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": bls_raw}
    ]

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Extract the content
    res_content = response.choices[0].message.content

    return jsonify({"content": res_content})

if __name__ == '__main__':
    app.run(debug=True)
