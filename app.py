import tempfile
import datetime

from flask                  import Flask, request, render_template, send_file, jsonify, redirect, url_for, session, flash, send_from_directory
from freddy                 import *
from pymongo                import MongoClient
from urllib.parse           import quote_plus
from werkzeug.utils         import secure_filename

usrnm = quote_plus('freddy')
pswrd = quote_plus('Freddy@123')

uri = f'mongodb+srv://{usrnm}:{pswrd}@cluster1.hnszelp.mongodb.net/'

client = MongoClient(uri)
db = client.users
collection = db.credentials

app = Flask(__name__)

app.secret_key = 'SOURAVRAWAT21102000'

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/logo.png')
def favicon():
    return send_from_directory('static', 'logo.png')

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method  == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        val = {
            "username": username,
            "password": password
        }
        user_exists = collection.find_one(val)
        if user_exists:
            session['current_user_name']=username
            return redirect(url_for('upload'))
        else:
            flash("Either the credentials are incorrect or the account does not exist.")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        val = {
            "username": username,
            "password": password
        }
        user_exists = collection.find_one(val)
        if user_exists:
            flash("User already exists. Please login instead.")
            return redirect(url_for('login'))
        else:
            collection.insert_one(val)
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/upload',methods=['GET','POST'])
def upload():
    username = session.get('current_user_name')
    if request.method == "POST":
        file = request.files['pdf_file']
        if file:
            filename = secure_filename(file.filename)
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            session['pdf_file_path'] = file_path
            return jsonify({'redirect_url': url_for('audio_response')})
    return render_template('upload.html',user=username)

@app.route('/audio_response', methods=['GET','POST'])
def audio_response():
    current_user_name = session.get('current_user_name')
    if request.method == 'POST':
        audio_file = request.files['audio']
        time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_file.save(f'Users Audios/{current_user_name}_{time}.wav')
        if audio_file:
            session['transcribed_text'] = speech_to_text(f"Users Audios/{current_user_name}_{time}.wav")
            pdf_file = session.get('pdf_file_path')
            db = creating_vectordb(pdf_file)
            qa = creating_retrieval_chain(db)
            session['llm_response']=groq_response(qa,session['transcribed_text'])
            text_to_speech(session['llm_response'],f'Freddy Audios/{current_user_name}_{time}.wav')
            audio_file_path = f'Freddy Audios/{current_user_name}_{time}.wav'
            return send_file(audio_file_path, mimetype='audio/wav')
    return render_template('response.html',user=current_user_name)

@app.route('/text_response', methods=['GET'])
def text_response():
    if 'transcribed_text' in session and 'llm_response' in session:
        return jsonify({"user_query":session['transcribed_text'],"llm_response": session['llm_response']})
    else:
        return jsonify({"error": "Transcribed text not found in session"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True,ssl_context='adhoc')

# pip install pyopenssl --- for running webpage on https://