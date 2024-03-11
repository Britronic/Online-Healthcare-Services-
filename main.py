from flask import Flask, render_template,url_for,redirect,request,session
import sqlite3
from datetime import datetime
import random
app = Flask(__name__)

app.secret_key = 'mysecretkey'
#  CREATE TABLE FUNCTION
def create_table():
	conn = sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('''
			CREATE TABLE IF NOT EXISTS doctorTable(
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				firstname TEXT,
				lastname TEXT,
				email TEXT,
				phonenumber TEXT,
				password TEXT,
				doctr_id TEXT
				)
		''')
	conn.commit()
	conn.close()

def add_column():
	conn = sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('ALTER TABLE doctorTable ADD COLUMN department TEXT')
	conn.commit()
	conn.close()
# FUNCTION TO INSERT DATA TO PATIENT TABLE - REGISTRATION
def insert_data(fullname, phonenumber,email,password,lastname,patient_id):
	conn = sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('''
			INSERT INTO patientTable (fullname,phonenumber,email,password,lastname,patient_id) VALUES (?,?,?,?,?,?)
		''',(fullname, phonenumber,email,password,lastname,patient_id)
		)
	conn.commit()
	conn.close()

# FUNCTION TO INSERT DATA TO APPOINTMENT TABLE
def appointment_data(fullname,doctor,date_,time_,insurance,status,department,patient_id):
	conn = sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('''
			INSERT INTO appointmentTable (fullname,doctor,date_,time_,insurance,status,department,patient_id) VALUES(?,?,?,?,?,?,?,?)
		''',(fullname,doctor,date_,time_,insurance,status,department,patient_id)
		)
	conn.commit()
	conn.close()

# Function To Validate
def validate_login(email,password):
	conn= sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute(
		 "SELECT * FROM patientTable WHERE email = ? AND password = ?",(email,password)
		)
	user_by_email = cursor.fetchone()
	
	cursor.execute(
		 "SELECT * FROM patientTable WHERE patient_id = ? AND password = ?",(email,password)
		)
	user_by_patient_id = cursor.fetchone()
	conn.close()

	if user_by_email:
		return {'id': user_by_email[0], 'firstname': user_by_email[1], 'email': user_by_email[3], 'patient_id':user_by_email[6]}
	elif user_by_patient_id:
		return {'id': user_by_patient_id[0],'firstname': user_by_patient_id[1],'email': user_by_patient_id[3], 'patient_id':user_by_patient_id[6]}
	else:
		None


@app.route('/')
def home():
	return render_template("index.html")


@app.route('/registration', methods=['GET','POST'])
def registration():
	if request.method == 'POST':
		fullname = request.form['Fullname']
		lastname = request.form['lastname']
		number = request.form['number']
		email = request.form['email']
		pass1 = request.form['password1']
		pass2 = request.form['password2']
		constant_string= fullname
		random_number = random.randint(1000,9999)
		patient_id= f'{constant_string}{random_number}'
		session['fullname'] = fullname
		# INSERT DATA INTO PATIENT TABLE
		insert_data(fullname,number,email,pass1,lastname,patient_id)
		return redirect(url_for('patientDashboard'))
		

	return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	condition_met = False
	if request.method == 'POST':
		name = request.form['email']
		password = request.form['password']
		# session['fullname'] = name
		user = validate_login(name,password)

		if user:
			session['fullname'] = user["firstname"]
			session['patient_id'] = user["patient_id"]
			
			return redirect(url_for('patientDashboard'))

		else:
			condition_met = True
	return render_template('login.html', condition_met=condition_met)
# ROUTES FOR PATIENT DASHBOARD
# 1 Dashbaord 

@app.route('/patientDashboard')
def patientDashboard():
	if 'fullname' in session:
		name = session['fullname']
		return render_template('patientdashboard.html',name=name)

	else:
		return redirect(url_for('login'))
# 2 Appointment Scheduling Route
@app.route('/AppointmentSchedule',methods=['GET', 'POST'])
def AppointmentSch():
	if 'fullname' in session:
		comfirm =False
		if request.method == 'POST':
			name = session['fullname']
			doctor = request.form['Doctor']
			date = request.form['date']
			time = request.form['time']
			insurance = request.form['insurance']
			status = "pending"
			department = request.form['department']
			patientid = session['patient_id']
			appointment_data(name,doctor,date,time,insurance,status,department,patientid)
			comfirm=True
		return render_template('appointmentscheduling.html', comfirm=comfirm)
	else:
		return redirect(url_for('login'))

# 3 Appointment History
@app.route('/AppointmentHistory')
def AppointmentHst():
	if 'fullname' in session:
		name = session['fullname']
		conn = sqlite3.connect('neema.db')
		cursor = conn.cursor()
		cursor.execute('SELECT * FROM appointmentTable WHERE fullname = ? ORDER BY date_ ASC', (name,) )
		appointments = cursor.fetchall()
		conn.close()
		return render_template('appointmenthistory.html', appointments=appointments)
	else:
		return redirect(url_for('login'))
# 4 E-Prescription
@app.route('/prescription')
def prescription():
	if 'fullname' in session:
		name = session['fullname']
		conn = sqlite3.connect('neema.db')
		cursor = conn.cursor()
		cursor.execute('SELECT * FROM prescription_request WHERE fullname = ?', (name,) )
		prescription = cursor.fetchall()
		conn.close()

		return render_template('prescribtion.html', prescription=prescription)
	else:
		return redirect(url_for('login'))
# 5 Profile Management
@app.route('/profile', methods=['GET','POST'])
def profile():
	if 'fullname' in session:
		name = session['fullname']
		conn = sqlite3.connect('neema.db')
		cursor = conn.cursor()
		cursor.execute('SELECT * FROM patientTable WHERE fullname = ?', (name,) )
		profile = cursor.fetchall()
		conn.close()

		if request.method == 'POST':
			name = session['fullname']
			new_password = request.form['new_password']
			new_email = request.form['new_email']
			conn = sqlite3.connect('neema.db')
			cursor = conn.cursor()
			alert1 = False
			alert2 = False		
			if new_password:
				cursor.execute('UPDATE patientTable SET password = ? WHERE fullname = ?', (new_password,name))
				alert1 = True
			if new_email:
				cursor.execute('UPDATE patientTable SET email = ? WHERE fullname = ?', (new_email,name))
				alert2 = True

			conn.commit()
			conn.close()
			return render_template('profile.html',profile=profile,alert1=alert1,alert2=alert2)
		return render_template('profile.html',profile=profile)
	else:
		return redirect(url_for('login'))
@app.route('/Feedback', methods=['GET', 'POST'])
def Feedback():
	if 'fullname' in session:
		comfirm= False
		if request.method == 'POST':
			name = session['fullname']
			msg = request.form['message']
			conn = sqlite3.connect('neema.db')
			cursor = conn.cursor()
			cursor.execute('''INSERT INTO feedbackTable (fullname, message) VALUES(?,?)''',(name,msg))
			conn.commit()
			conn.close()
			comfirm = True
		return render_template('feedback.html',comfirm=comfirm)
	else:
		return redirect(url_for('login'))
@app.route('/logout')
def logout():
	session.pop('fullname', None)
	session.pop('patient_id', None)
	return redirect(url_for('home'))
# 
# 
# DOCTOR SECTION 
# 
# 
# FUNCTION TO RETRIEVE DATA FROM TABLE FOR DASHBOARD DISPLAY
# 1 COMMENTS RETRIEVAL
def get_comments():
	conn = sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('SELECT fullname,message FROM feedbackTable')
	comments_ = cursor.fetchall()
	conn.close()
	return comments_
# FUNTION TO RETRIEVE DOCTOR NAME
def docName():
	doctor_id_ = session['doctor_id']
	conn =sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('SELECT firstname FROM doctorTable WHERE doctr_id = ?',(doctor_id_,))
	doctor_name= cursor.fetchone()[0]
	return doctor_name

#  2 RECENT APPOINTMENT RETRIEVING
def fetch_appointments1():
	doctor_name = docName()
	conn = sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('SELECT id,fullname,doctor,date_,status FROM appointmentTable WHERE doctor = ? ORDER BY date_ ASC LIMIT 10',(doctor_name,))
	appointments =cursor.fetchall()
	return appointments

#  2 RECENT APPOINTMENT RETRIEVING
def fetch_appointments():
	conn = sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('SELECT id,fullname,doctor,date_,status FROM appointmentTable  ORDER BY date_ ASC LIMIT 10')
	appointments =cursor.fetchall()
	return appointments

# 3 GET TOTAL PATIENTS
def fetch_patient_count():
	conn = sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('SELECT COUNT(*) FROM patientTable')
	counts =cursor.fetchone()[0]
	conn.close()
	return counts

# 4 GET TOTAL Appointments
def fetch_appointment_count():
	conn = sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('SELECT COUNT(*) FROM appointmentTable')
	counts =cursor.fetchone()[0]
	conn.close()
	return counts

# 5 GET TOTAL Remarks
def fetch_feedback_count():
	conn = sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('SELECT COUNT(*) FROM feedbackTable')
	counts =cursor.fetchone()[0]
	conn.close()
	return counts
# 6 GET TOTAL DOCTORS
def fetch_doctor_count():
	conn = sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('SELECT COUNT(*) FROM doctorTable')
	counts =cursor.fetchone()[0]
	conn.close()
	return counts
# Function To Validate DOCTOR LOGIN
def doc_validate_login(username,password):
	conn= sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute(
		 "SELECT * FROM doctorTable WHERE email = ? AND password = ?",(username,password)
		)
	user_by_email = cursor.fetchone()
	
	cursor.execute(
		 "SELECT * FROM doctorTable WHERE doctr_id = ? AND password = ?",(username,password)
		)
	user_by_doctr_id = cursor.fetchone()
	conn.close()

	if user_by_email:
		return {'id': user_by_email[0], 'firstname': user_by_email[1], 'email': user_by_email[3], 'doctr_id':user_by_email[6]}
	elif user_by_doctr_id:
		return {'id': user_by_doctr_id[0],'firstname': user_by_doctr_id[1],'email': user_by_doctr_id[3], 'doctr_id':user_by_doctr_id[6]}
	else:
		None


# DOCTOR LOGIN ROUTE 
@app.route('/doctor-login', methods=['GET','POST'])
def doclogin():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		#  HANDLE VALIDATION
		doctor = doc_validate_login(username,password)

		if doctor:
			session['doctor_id'] = doctor['doctr_id']
			session['doctor_name'] =doctor['firstname']
			return redirect(url_for('doctordashboard'))
		else:
			alert1 =True
			return render_template('doclogin.html',alert1=alert1)
	return render_template('doclogin.html')
# FUNCTION TO INSERT DATA TO PATIENT TABLE - REGISTRATION
def doc_insert_data(firstname,lastname, email,phonenumber,password,doctr_id,department):
	conn = sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('''
			INSERT INTO doctorTable (firstname,lastname, email,phonenumber,password,doctr_id,department) VALUES (?,?,?,?,?,?,?)
		''',(firstname,lastname, email,phonenumber,password,doctr_id,department)
		)
	conn.commit()
	conn.close()
# DOCTOR REGISTRATION
@app.route('/doctor-registration', methods=['GET','POST'])
def docregister():
	if request.method == 'POST':
		firstname = request.form['firstname']
		lastname = request.form['lastname']
		email =request.form['email']
		department =request.form['department']
		phonenumber = request.form['phonenumber']
		password1 = request.form['password1']
		password2 = request.form['password2']
		constant_string= firstname
		random_number= random.randint(100,999)
		doctr_id = f'{constant_string}{random_number}'
		if password1 == password2:

			# Enter The Data into table
			doc_insert_data(firstname,lastname,email,phonenumber,password1,doctr_id,department)
			return redirect(url_for('doctordashboard'))
		else:
			alert1 = True
			return render_template('docregistration.html', alert1=alert1)

	return render_template('docregistration.html')

# Doctor Dashboard Route
@app.route('/doctordashboard')
def doctordashboard():
	if 'doctor_id' in session:
		doctor_name = docName()
		doctor= fetch_doctor_count()
		comments=get_comments()
		appointments=fetch_appointments()
		totalappointments =fetch_appointment_count()
		totalpatients = fetch_patient_count()
		feedback=fetch_feedback_count()
		return render_template('docDashboard.html',doctor_name=doctor_name,doctor=doctor, totalappointments=totalappointments, totalpatients=totalpatients,comments=comments,appointments=appointments,feedback=feedback)
	else:
		return redirect(url_for('doclogin'))

# Appointment Route
@app.route('/appointmentmanagement')
def appointmentmng():
	if 'doctor_id' in session:
		appointments = fetch_appointments1()
		doctor_name = docName()
		return render_template('appointmentmanagement.html',doctor_name=doctor_name,appointments=appointments)
	else:
		return redirect(url_for('doclogin'))
# Route To Update Appointment Status
@app.route('/update/<int:appointment_id>/<action>')
def update_status(appointment_id,action):
	valid_action = ['accept' ,'deny']
	if action not in valid_action:
		pass
	conn = sqlite3.connect('neema.db')
	cursor = conn.cursor()
	if action == 'accept':
		cursor.execute('UPDATE appointmentTable SET status = ? WHERE id =?',('Accepted',appointment_id))
	elif action == 'deny':
		cursor.execute('UPDATE appointmentTable SET status = ? WHERE id =?',('Denied',appointment_id))

	conn.commit()
	conn.close()
	return redirect(url_for('appointmentmng'))


# E-Prescription Route
@app.route('/e-prescription', methods=['GET','POST'])
def eprescription():
	if 'doctor_id' in session:
		if request.method == 'POST':
			patient_id = request.form['full_name']
			alert= False
			status= "Accepted"
			session['id_patient'] = patient_id
			conn =sqlite3.connect('neema.db')
			cursor = conn.cursor()
			cursor.execute('SELECT * FROM appointmentTable WHERE patient_id = ? AND status = ?',(patient_id,status))
			details = cursor.fetchone()
			conn.close()

			if details:
				return render_template('ePrescribtion.html',patient_details=details)
			else:
				alert= True
				return render_template('ePrescribtion.html', alert=alert)

		return render_template('ePrescribtion.html')
	else:
		return redirect(url_for('doclogin'))
# SAVE PRESRIPTION
@app.route('/save_prescription',methods=['GET','POST'])
def save_prescription():
	if 'doctor_id' in session:
		fullname=request.form['full_name']
		doctor=request.form['doctor']
		medication =request.form['medication']
		dosage = request.form['dosage']
		instructions = request.form['instructions']
		timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		alert1 =False
		patient_id=session['id_patient']
		conn =sqlite3.connect('neema.db')
		cursor =conn.cursor()
		cursor.execute(
			'''
				INSERT INTO prescription_request (fullname,doctor,medication,dosage,instruction,timestamp_,patient_id) VALUES (?,?,?,?,?,?,?)

			''',
			(fullname,doctor,medication,dosage,instructions,timestamp,patient_id))
		cursor.execute('DELETE  FROM appointmentTable WHERE patient_id =?',(patient_id,))
		conn.commit()
		conn.close()
		alert1=True
		return render_template('ePrescribtion.html',alert1=alert1)
	else:
		return redirect(url_for('doclogin'))


# Patient Route
@app.route('/patientrecord', methods=['GET','POST'])
def patientrecords():
	if 'doctor_id' in session:
		if request.method == 'POST':
			patient_id =request.form['patient_id']

			# patientdetails = get_patient_details(patient_id)
			# appointments = get_patient_appointment(patient_id)
			# prescription = get_patient_prescription(patient_id)
			conn =sqlite3.connect('neema.db')
			cursor = conn.cursor()
			cursor.execute('SELECT * FROM patientTable WHERE patient_id =?',(patient_id,))
			patient_details = cursor.fetchone()
			
			cursor.execute('SELECT * FROM appointmentTable WHERE patient_id =?',(patient_id,))
			appointments = cursor.fetchone()

			cursor.execute('SELECT * FROM prescription_request WHERE patient_id =?',(patient_id,))
			prescription = cursor.fetchone()

			conn.close()


			if patient_details:
				return render_template('patientrecords.html', patient_details=patient_details,appointments=appointments,prescription=prescription)
			else:
				pass
		return render_template('patientrecords.html')
	else:
		return redirect(url_for('doclogin'))
# Function For patient Details
def get_patient_details(patient_id):
	conn =sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM patientTable WHERE patient_id =?',(patient_id,))
	patient_details = cursor.fetchone()
	conn.close()
	return patient_details

# Function For patient appoitnment Details
def get_patient_appointment(patient_id):
	conn =sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM appointmentTable WHERE patient_id =?',(patient_id,))
	appointments = cursor.fetchone()
	conn.close()
	return appointments

# Function For patient prescription Details
def get_patient_prescription(patient_id):
	conn =sqlite3.connect('neema.db')
	cursor = conn.cursor()
	cursor.execute('SELECT * FROM prescription_request WHERE patient_id =?',(patient_id,))
	prescription = cursor.fetchone()
	conn.close()
	return prescription


# Appointment Reminder Route
@app.route('/appointmentreminder')
def appointmentreminder():
	return render_template('docreminder.html')
# Feedback Route
@app.route('/feedbackmng')
def feedbackmng():
	if 'doctor_id' in session:
		feedback=get_comments()
		return render_template('docfeedback.html', feedback=feedback)
	else:
		return redirect(url_for('doclogin'))

# Doctore Profile Route
@app.route('/doctor-profile',methods=['GET','POST'])
def docprofile():
	if 'doctor_id' in session:
		doctor_id_ = session['doctor_id']
		conn =sqlite3.connect('neema.db')
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM doctorTable WHERE  doctr_id = ?",(doctor_id_,))
		doctor =cursor.fetchone()

		if request.method == 'POST':
			email = request.form['email']
			password = request.form['password']
			phonenumber = request.form['phonenumber']

			cursor.execute("UPDATE doctorTable SET email = ?, password = ?, phonenumber = ? WHERE doctr_id = ?",(email,password,phonenumber,doctor_id_))
			conn.commit()
			return redirect(f'/doctor-profile')
		conn.close()
		return render_template('docprofile.html',doctor=doctor)
	else:
		return redirect(url_for('doclogin'))
# Logout Route
@app.route('/doclogout')
def doclogout():
	session.clear()
	return redirect(url_for('home'))

if __name__ == "__main__":
	create_table()
	# docName()

	app.run(debug=True)
