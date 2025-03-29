# import the necessary packages
from flask import Flask, render_template, redirect, url_for, request,session,Response
from Intrusion import *
from network_intrusion import *
from sql_injection import *
import pickle
from phishing import *
import pickle
import tensorflow as tf
from keras.models import Sequential, Model, model_from_json, load_model
from keras.preprocessing import sequence
import json
from string import printable
import sqlite3

# load json and create model
json_file = open('model3conv_200.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("model3conv_200.h5")
print("Loaded model from disk")

name = ''

app = Flask(__name__)

app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', methods=['GET', 'POST'])
def landing():
	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	global name
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT Name from Users WHERE Email='{email}' AND password = '{password}';")
		try:
			name = cursorObj.fetchone()[0]
			return redirect(url_for('home'))
		except:
			error = "Invalid Credentials Please try again..!!!"
			return render_template('login.html',error=error)
	return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		if request.form['sub']=='Submit':
			name = request.form['name']
			email = request.form['email']
			password = request.form['password']
			rpassword = request.form['rpassword']
			pet = request.form['pet']
			if(password != rpassword):
				error='Password dose not match..!!!'
				return render_template('register.html',error=error)
			try:
				con = sqlite3.connect('mydatabase.db')
				cursorObj = con.cursor()
				cursorObj.execute(f"SELECT Name from Users WHERE Email='{email}' AND password = '{password}';")
			
				if(cursorObj.fetchone()):
					error = "User already Registered...!!!"
					return render_template('register.html',error=error)
			except:
				pass
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")			
			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS Users (Date text,Name text,Email text,password text,pet text)")
			cursorObj.execute("INSERT INTO Users VALUES(?,?,?,?,?)",(dt_string,name,email,password,pet))
			con.commit()

			return redirect(url_for('login'))

	return render_template('register.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
	error = None
	global name
	if request.method == 'POST':
		email = request.form['email']
		pet = request.form['pet']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT password from Users WHERE Email='{email}' AND pet = '{pet}';")
		
		try:
			password = cursorObj.fetchone()
			#print(password)
			error = "Your password : "+password[0]
		except:
			error = "Invalid information Please try again..!!!"
		return render_template('forgot-password.html',error=error)
	return render_template('forgot-password.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
	global name
	return render_template('home.html',name=name)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	return render_template('dashboard.html',name=name)

@app.route('/sql', methods=['GET', 'POST'])
def sql():
	if request.method == 'POST':
		query = request.form['query']
		feat = sqlFeatures(query)
		# load the model from disk
		loaded_model = pickle.load(open('sql.sav', 'rb'))
		sql_r = loaded_model.predict(feat)
		sql_r = 'SQL Injection' if sql_r[0]==1 else 'Normal'
		return render_template('sql.html',sql_r=sql_r,name=name)

	return render_template('sql.html',name=name)

@app.route('/xss', methods=['GET', 'POST'])
def xss():
	if request.method == 'POST':
		sentence = request.form['script']
		pred = detect_xss(sentence)

		return render_template('xss.html',xss_r=pred,name=name)

	return render_template('xss.html',name=name)

@app.route('/phishing', methods=['GET', 'POST'])
def phishing():
	if request.method == 'POST':
		url = request.form['url']
		# Step 1: Convert raw URL string in list of lists where characters that are contained in "printable" are stored encoded as integer 
		url_int_tokens = [[printable.index(x) + 1 for x in url if x in printable]]
		# Step 2: Cut URL string at max_len or pad with zeros if shorter
		max_len=75
		X = sequence.pad_sequences(url_int_tokens, maxlen=max_len)
		y_prob = loaded_model.predict(X,batch_size=1)
		result = 'Legitimate URL' if y_prob[0][0]<0.5 else 'Phishing URL'

		return render_template('phishing.html',url_r=result,name=name)

	return render_template('phishing.html',name=name)

@app.route('/intrusion', methods=['GET', 'POST'])
def intrusion():	
	if request.method == 'POST':
		packet = 	Convert(request.form['packet'])
		test_df = [float(i) for i in packet]
		result = predict([test_df])
		print(result)
		return render_template('intrusion.html',result1=result[0],result2=result[1],result3=result[2],name=name)


	return render_template('intrusion.html',name=name)



# No caching at all for API endpoints.
@app.after_request
def add_header(response):
	# response.cache_control.no_store = True
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response


if __name__ == '__main__' and run:
	app.run(host='0.0.0.0', debug=True, threaded=True)
