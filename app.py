import os
from urllib import parse
import requests
from flask import Flask, session,redirect, request, url_for, render_template
from flask_session import Session
from requests_oauthlib import OAuth2Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine, exc
from sqlalchemy.sql import text


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# engine = create_engine("mysql+pymysql://c391tujwolvmij5a:tqkzvprrc96kcm2g@frwahxxknm9kwy6c.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/rjb11pca4j89kh0x")
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key = os.urandom(24)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# OURA_CLIENT_ID ="GDXZT26FQ25TSK7M"
# OURA_CLIENT_SECRET = "TRMFHOI2T3BYRYRP7POC62KUYN37NON4"
OURA_CLIENT_ID     = os.getenv('OURA_CLIENT_ID')
OURA_CLIENT_SECRET = os.getenv('OURA_CLIENT_SECRET')

OURA_AUTH_URL = 'https://cloud.ouraring.com/oauth/authorize'
OURA_TOKEN_URL = 'https://api.ouraring.com/oauth/token'
OURA_CALLBACK = 'https://ourastudy.herokuapp.com/callback' #"http://119.45.40.139:8027/callback"
OURA_SLEEP = 'https://ourastudy.herokuapp.com/sleep'
global user_str


@app.route('/login', methods = ['POST'])
def oura_login():
    """Login to the Oura cloud.
    This will redirect to the login page 
    of the OAuth provider in our case the 
    Oura cloud's login page

    """
    if request.method == 'POST':
        global user_str
        user_str = request.form['fname']
    # print(OURA_CLIENT_ID)

    oura_session = OAuth2Session(OURA_CLIENT_ID)
    # URL for Oura's authorization page for specific client
    authorization_url, state = oura_session.authorization_url(OURA_AUTH_URL)
    # print("authorization_url",authorization_url)
    session['oauth_state'] = state
    # print("oauth_state",session['oauth_state'])
    newUrl = "{}&redirect_uri={}".format(authorization_url,parse.quote(OURA_CALLBACK))
    
    return redirect(newUrl)
# response_type=code&client_id=E55QJ2DGMZUXK6TN&redirect_uri=https%3A%2F%2Fexample.com%2Fcallback&scope=email+personal&state=3PgHyjNECEu5YgTQP33NC5tZJ0onm2
# response_type=code&client_id=GDXZT26FQ25TSK7M&state=oz0gfSKEwtabRPHyp5Xu0OxrfH1DnF

@app.route('/callback')
def callback():
    """Callback page
    Get the acces_token from response url from Oura. 
    Redirect to the sleep data page.
    """
    print("callback")
    # oura_session = OAuth2Session(OURA_CLIENT_ID, state=request.args.get('state'))
    payload = f"grant_type=authorization_code&code={request.args.get('code')}&client_id={OURA_CLIENT_ID}&client_secret={OURA_CLIENT_SECRET}&redirect_uri={OURA_CALLBACK}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57",
        "content-type": "application/x-www-form-urlencoded"
    }

    response = requests.request("POST", OURA_TOKEN_URL, data=payload, headers=headers)
    # return response.text
    access_token = response.json()['access_token']
    refresh_token = response.json()['refresh_token']
    oauth = {
        "access_token":access_token,
        "refresh_token":refresh_token,
    }
    session['oauth'] = oauth
    # print(session['oauth'])
    return redirect(url_for('.sleep'))

@app.route('/sleep')
def sleep():
    oauth_access_token = session['oauth']['access_token']
    # add 
    oauth_refresh_token = session['oauth']['refresh_token']

    # Add token to the database
    # save_token = user_token(user_id = user_str,access_token = oauth_access_token, refresh_token = oauth_refresh_token)
    user = db.execute(text(f"SELECT * FROM tokens WHERE user_id = '{user_str}'"))
    print("user--->",[item for item in user])
    if len([item for item in user]) == 0:
    # add 
    #     db.execute(text(f"INSERT INTO tokens (user_id, access_token, refresh_token) VALUES ('{user_str}', '{oauth_access_token}', '{oauth_refresh_token}')"))
        db.execute(text(f"INSERT INTO tokens (user_id, oauth_token) VALUES ('{user_str}', '{oauth_access_token}')"))
    else:
        db.execute(text(f"UPDATE tokens SET oauth_token = '{oauth_access_token}'  WHERE user_id = '{user_str}'"))
        # db.execute(text(f"UPDATE tokens SET access_token = '{oauth_access_token}'  WHERE user_id = '{user_str}'"))
        # db.execute(text(f"UPDATE tokens SET refresh_token = '{oauth_refresh_token}'  WHERE user_id = '{user_str}'"))
    db.commit()
    # with open('user_tokens.txt', 'a') as f:
    #     f.write(user_str +': ' + oauth_access_token + oauth_refresh_token + '\n')
    return  render_template('exit.html')

@app.route('/')
def home():
    """Welcome page of the sleep data app.
    """
    return render_template('welcome.html') # "<h1>Welcome to your Oura app</h1>"

@app.route('/oauth/token')
def oauthToekn():
    """Welcome page of the sleep data app.
    """
    return render_template('welcome.html') # "<h1>Welcome to your Oura app</h1>"


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=9090)

