# from flask import * 
from flask import render_template, Blueprint, request, redirect, session
from .database import _queryAllMembers, _isMember, _addMember, _queryOneMember
from .extensions import mysql
import MySQLdb.cursors
from datetime import datetime


hospital = Blueprint('hospital', __name__)


@hospital.route('/')
def index():
    return render_template('index.html')


@hospital.route('/signup', methods=['POST', 'GET'])
def signup():
    tryMessage = False
    user = False
    if request.method == 'POST':
        if request.form['password1'] == request.form['password2']:
            text = 'the passwords match'
            tryMessage = ''
            sql = f"select id from `Employee` where id = '{request.form['id']}'"
            person = _isMember(sql)
            if person:
                user = True
                return render_template('signup.html', user=user)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('insert into `Employee`\
                           (id, fname, lname, password, address, telephone, email, dateEmployed, rank, city)\
                           values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (request.form['id'], request.form['fname'], request.form['lname'], request.form['password1'], request.form['address'], 
                            request.form['telephone'], request.form['email'], request.form['dateEmployed'], request.form['rank'], request.form['city'], ))
            mysql.connection.commit()
            session['id'] = request.form['id']
            return redirect('/menu')
        else:
            tryMessage = True
            return render_template('signup.html', tryMessage=tryMessage)
    return render_template('new/signup.html')


@hospital.route('/signin', methods=['POST', 'GET'])
def signin():
    isCorrect = False
    isUser = False
    if request.method == 'POST':
        sql = f"select * from `Employee` where id = '{request.form['id']}'"
        user1 = _isMember(sql)
        if user1:
            user = _queryOneMember(sql)
            if request.form['password'] == user['password']:
                session['id'] = request.form['id']
                return redirect('/menu')
            isCorrect = True
            return render_template('signin.html', isCorrect=isCorrect)
        isUser = True
        return render_template('signin.html', isUser=isUser)
    return render_template('new/signin.html')


@hospital.route('/new patient', methods=['POST', 'GET'])
def new_patient():
    user = False
    txt = ''
    if not session.get('id'):
        return redirect('/signin')
    elif request.method == 'POST':
        sql = f"select patientId from `Patient` where patientId = '{request.form['id']}'"
        patient = _isMember(sql)
        if patient:
            txt = f"Patient {request.form['id']} already exists"
            return redirect(f'/success/{txt}')
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("insert into `Patient`\
                           (patientId, fname, lname, paymentMethod, DOB, email, tel, address, city)\
                           values(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (request.form['id'], request.form['fname'], request.form['lname'], request.form['paymentMethod'], 
                            request.form['DOB'], request.form['email'], request.form['telephone'], request.form['address'],
                            request.form['city'], )
            )
            mysql.connection.commit()
            return redirect(f"/patient success/{request.form['fname']}/new patient/{request.form['id']}")
    return render_template('new/patient.html')


@hospital.route('/patient success/<name>/<routeType>/<id>')
def patient_success(name, routeType, id):
    if not session.get('id'):
        return redirect('/signin')
    return render_template('success/success.html', name=name, routeType=routeType, id=id)


@hospital.route('/success/<name>/<routeType>')
def success(name, routeType):    
    if not session.get('id'):
        return redirect('/signin')
    return render_template('success/success.html', name=name, routeType=routeType)


@hospital.route('/menu')
def menu():
    if not session.get('id'):
        return redirect('/signin')
    return render_template('menu.html')


@hospital.route('/all patients')
def all_patients():
    if not session.get('id'):
        return redirect('/signin')
    sql = "select * from `Patient` order by fname"
    patients = _queryAllMembers(sql)
    return render_template('all/patients.html', patients=patients)


@hospital.route('/edit patient/<id>', methods=['POST','GET'])
def edit_patient(id):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Patient` where patientId='{id}'"
    patient = _queryOneMember(sql)
    if request.method == 'POST':
        sql = f"update `Patient` set\
                fname = '{request.form['fname']}', lname = '{request.form['lname']}', paymentMethod = '{request.form['paymentMethod']}',\
                DOB = '{request.form['DOB']}', email = '{request.form['email']}', tel = '{request.form['telephone']}', address = '{request.form['address']}', city = '{request.form['city']}'\
                where patientId = '{id}'"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)        
        mysql.connection.commit()
        return redirect(f"/detail patient/{id}")
    return render_template('edit/patients.html', patient=patient)


@hospital.route('/detail patient/<id>')
def detail_patient(id):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Patient` where patientId='{id}'"
    patient = _queryOneMember(sql)
    sql1 = f"select * from `Patient_has_Alergies` where Patient_patientId='{id}'"
    allergies =  _queryAllMembers(sql1)
    sql2 = f"select * from `Vaccine_has_Patient` where Patient_patientId='{id}'"
    vaccines = _queryAllMembers(sql2)
    sql3= f"select * from `Treatment` where Patient_patientId='{id}'"
    treatment = _queryAllMembers(sql3)
    return render_template('detail/patients.html', patient=patient, allergies=allergies, vaccines=vaccines, treatment=treatment)


@hospital.route('/search patient', methods=['GET', 'POST'])
def search_patient():
    if not session.get('id'):
        return redirect('/signin')
    elif request.method == 'POST':
        name = request.form['searchItem']    
        if request.form['searchType'] == 'fname' or request.form['searchType'] == 'default':        
            sql = f"select * from `Patient` where fname REGEXP '{name}'"
        elif request.form['searchType'] == 'lname':
            sql = f"select * from `Patient` where lname REGEXP '{name}'"
        elif request.form['searchType'] == 'patientId':
            sql = f"select * from `Patient` where patientId REGEXP '{name}'"
        elif request.form['searchType'] == 'email':
            sql = f"select * from `Patient` where email REGEXP '{name}'"
        patients = _queryAllMembers(sql)        
        return render_template('search/patients.html', patients=patients)
    return render_template('search/patients.html')


@hospital.route('/new disease', methods=['POST', 'GET'])
def new_disease():
    user = False
    txt = ''
    if not session.get('id'):
        return redirect('/signin')
    elif request.method == 'POST':
        sql = f"select dieseaseName from `Diseases` where dieseaseName = '{request.form['name']}'"
        patient = _isMember(sql)
        if patient:
            txt = f"Patient {request.form['name']} already exists"
            return redirect(f'/success/{txt}')
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("insert into `Diseases`\
                           (dieseaseName, description, symptoms, spread, treatment, prevention, typeofCause, nameofCause)\
                           values(%s, %s, %s, %s, %s, %s, %s, %s)",
                           (request.form['name'], request.form['description'], request.form['symptoms'], request.form['spread'], 
                            request.form['treatment'], request.form['prevention'], request.form['typeofCause'], request.form['nameofCause'],)
            )
            mysql.connection.commit()
            return redirect(f"/success/{request.form['name']}/new disease")
    return render_template('new/disease.html')


@hospital.route('/all diseases')
def all_diseases():
    if not session.get('id'):
        return redirect('/signin')
    sql = "select * from `Diseases`"
    diseases = _queryAllMembers(sql)
    return render_template('all/diseases.html', diseases=diseases)


@hospital.route('/edit disease/<dieseaseName>', methods=['POST', 'GET'])
def edit_disease(dieseaseName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Diseases` where dieseaseName='{dieseaseName}'"
    disease = _queryOneMember(sql)
    if request.method == 'POST':
        sql = f"update `Diseases` set\
            dieseaseName = '{request.form['name']}', description = '{request.form['description']}', symptoms = '{request.form['symptoms']}', spread = '{request.form['spread']}',\
            treatment = '{request.form['treatment']}', prevention = '{request.form['prevention']}', typeofCause = '{request.form['typeofCause']}', nameofCause = '{request.form['nameofCause']}'\
            where dieseaseName = '{request.form['name']}'"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)        
        mysql.connection.commit()
        return redirect(f'/detail disease/{dieseaseName}')
    return render_template('edit/diseases.html', disease=disease)


@hospital.route('/detail disease/<dieseaseName>')
def detail_disease(dieseaseName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Diseases` where dieseaseName='{dieseaseName}'"
    disease = _queryOneMember(sql)
    sql1 = f"select Vaccine_vaccineName from `Diseases_has_Vaccine` where Diseases_dieseaseName = '{dieseaseName}'"
    vaccines = _queryAllMembers(sql1)
    sql2 = f"select Drugs_drugName from `Diseases_has_Drugs` where Diseases_dieseaseName = '{dieseaseName}'"
    drugs = _queryAllMembers(sql2)
    prevention = disease['prevention'].split('\n')
    symptoms = disease['symptoms'].split('\n')
    return render_template('detail/diseases.html', disease=disease, prevention=prevention, symptoms=symptoms, vaccines=vaccines, drugs=drugs)


@hospital.route('/search disease', methods=['GET', 'POST'])
def search_disease():
    if not session.get('id'):
        return redirect('/signin')
    elif request.method == 'POST':
        name = request.form['searchItem']    
        if request.form['searchType'] == 'dieseaseName' or request.form['searchType'] == 'default':        
            sql = f"select * from `Diseases` where dieseaseName REGEXP '{name}'"
        elif request.form['searchType'] == 'typeofCause':
            sql = f"select * from `Diseases` where typeofCause REGEXP '{name}'"
        elif request.form['searchType'] == 'nameofCause':
            sql = f"select * from `Diseases` where nameofCause REGEXP '{name}'"
        diseases = _queryAllMembers(sql)        
        return render_template('search/diseases.html', diseases=diseases)
    return render_template('search/diseases.html')


@hospital.route('/new allergies', methods=['GET', 'POST'])
def new_allergies():
    user = False
    txt = ''
    if not session.get('id'):
        return redirect('/signin')
    elif request.method == 'POST':
        sql = f"select alergyName from `Alergies` where alergyName = '{request.form['alergyName']}'"
        patient = _isMember(sql)
        if patient:
            txt = f"Patient {request.form['alergyName']} already exists"
            return redirect(f'/success/{txt}')
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("insert into `Alergies`\
                           (alergyName, effects, antiHistamine, allergen)\
                           values(%s, %s, %s, %s)",
                           (request.form['alergyName'], request.form['effects'], request.form['antiHistamine'], request.form['allergen'],)
            )
            mysql.connection.commit()
            return redirect(f"/success/{request.form['alergyName']}")
    return render_template('new/allergies.html')


@hospital.route('/all allergies')
def all_allergies():
    if not session.get('id'):
        return redirect('/signin')
    sql = "select * from `Alergies`"
    allergies = _queryAllMembers(sql)
    return render_template('all/allergies.html', allergies=allergies)


@hospital.route('/edit allergies/<alergyName>', methods=['POST', 'GET'])
def edit_allergies(alergyName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Alergies` where alergyName = '{alergyName}'"
    alergy = _queryOneMember(sql)
    if request.method == 'POST':
        sql = f"update `Alergies` set \
            alergyName = '{request.form['alergyName']}', effects = '{request.form['effects']}', antiHistamine = '{request.form['antiHistamine']}', allergen = '{request.form['allergen']}'\
            where alergyName = '{request.form['alergyName']}'"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)        
        mysql.connection.commit()
        return redirect(f"/detail allergies/{request.form['alergyName']}")
    return render_template('edit/allergies.html', alergy=alergy)


@hospital.route('/detail allergies/<alergyName>')
def detail_allergies(alergyName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Alergies` where alergyName = '{alergyName}'"
    alergy = _queryOneMember(sql)
    effects = alergy['effects'].split('\n')
    return render_template('detail/allergies.html', alergy=alergy, effects=effects)


@hospital.route('/search allergies', methods=['GET', 'POST'])
def search_allergies():
    if not session.get('id'):
        return redirect('/signin')
    elif request.method == 'POST':
        name = request.form['searchItem']    
        if request.form['searchType'] == 'alergyName' or request.form['searchType'] == 'default':        
            sql = f"select * from `Alergies` where alergyName REGEXP '{name}'"
        elif request.form['searchType'] == 'allergen':
            sql = f"select * from `Alergies` where allergen REGEXP '{name}'"
        elif request.form['searchType'] == 'antiHistamine':
            sql = f"select * from `Alergies` where antiHistamine REGEXP '{name}'"
        allergies = _queryAllMembers(sql)        
        return render_template('search/allergies.html', allergies=allergies)
    return render_template('search/allergies.html')


@hospital.route('/new drug', methods=['POST', 'GET'])
def new_drugs():
    user = False
    txt = ''
    if not session.get('id'):
        return redirect('/signin')
    elif request.method == 'POST':
        sql = f"select drugName from `Drugs` where drugName = '{request.form['drugName']}'"
        patient = _isMember(sql)
        if patient:
            txt = f"Patient {request.form['drugName']} already exists"
            return redirect(f'/success/{txt}')
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("insert into `Drugs`\
                           (drugName, drugManufacturer)\
                           values(%s, %s)",
                           (request.form['drugName'], request.form['drugManufacturer'],)
            )
            mysql.connection.commit()
            return redirect(f"/success/{request.form['drugName']}/new drug")
    return render_template('new/drugs.html')


@hospital.route('/all drugs')
def all_drugs():
    if not session.get('id'):
        return redirect('/signin')
    sql = "select * from `Drugs`"
    drugs = _queryAllMembers(sql)
    return render_template('all/drugs.html', drugs=drugs)


@hospital.route('/edit drug/<drugName>', methods=['POST', 'GET'])
def edit_drug(drugName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Drugs` where drugName = '{drugName}'"
    drug = _queryOneMember(sql)
    if request.method == 'POST':
        sql = f"update `Drugs` set \
            drugName = '{request.form['drugName']}', drugManufacturer = '{request.form['drugManufacturer']}'\
            where drugName = '{request.form['drugName']}'"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)        
        mysql.connection.commit()
        return redirect(f"/detail drug/{drugName}")
    return render_template('edit/drugs.html', drug=drug)


@hospital.route('/detail drug/<drugName>')
def detail_drug(drugName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Drugs` where drugName = '{drugName}'"
    drug = _queryOneMember(sql)
    return render_template('detail/drugs.html', drug=drug)


@hospital.route('/search drugs', methods=['GET', 'POST'])
def search_drug():
    if not session.get('id'):
        return redirect('/signin')
    if request.method == 'POST':
        name = request.form['searchItem']    
        if request.form['searchType'] == 'drugName' or request.form['searchType'] == 'default':        
            sql = f"select * from `Drugs` where drugName REGEXP '{name}'"
        elif request.form['searchType'] == 'drugManufacturer':
            sql = f"select * from `Drugs` where drugManufacturer REGEXP '{name}'"
        drugs = _queryAllMembers(sql)        
        return render_template('search/drugs.html', drugs=drugs)
    return render_template('search/drugs.html')


@hospital.route('/new vaccine', methods=['POST', 'GET'])
def new_vaccine():
    user = False
    txt = ''
    if not session.get('id'):
        return redirect('/signin')
    elif request.method == 'POST':
        sql = f"select vaccineName from `Vaccine` where vaccineName = '{request.form['vaccineName']}'"
        patient = _isMember(sql)
        if patient:
            txt = f"Patient {request.form['vaccineName']} already exists"
            return redirect(f'/success/{txt}')
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("insert into `Vaccine`\
                           (vaccineName, ageAdministered, manufacturer)\
                           values(%s, %s, %s)",
                           (request.form['vaccineName'], request.form['ageAdministered'], request.form['manufacturer'],)
            )
            mysql.connection.commit()
            return redirect(f"/success/{request.form['vaccineName']}/new vaccine")
    return render_template('new/vaccines.html')


@hospital.route('/all vaccines')
def all_vaccines():
    if not session.get('id'):
        return redirect('/signin')
    sql = "select * from `Vaccine`"
    vaccines = _queryAllMembers(sql)
    return render_template('all/vaccines.html', vaccines=vaccines)


@hospital.route('/edit vaccine/<vaccineName>', methods=['POST', 'GET'])
def edit_vaccine(vaccineName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Vaccine` where vaccineName = '{vaccineName}'"
    vaccine = _queryOneMember(sql)
    if request.method == 'POST':
        sql = f"update `Vaccine` set \
            vaccineName = '{request.form['vaccineName']}' , ageAdministered = '{request.form['ageAdministered']}', manufacturer = '{request.form['manufacturer']}' \
            where vaccineName = '{request.form['vaccineName']}'"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)        
        mysql.connection.commit()
        return redirect(f"/detail vaccine/{vaccineName}")
    return render_template('edit/vaccines.html', vaccine=vaccine)


@hospital.route('/detail vaccine/<vaccineName>')
def detail_vaccine(vaccineName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Vaccine` where vaccineName = '{vaccineName}'"
    vaccine = _queryOneMember(sql)
    return render_template('detail/vaccines.html', vaccine=vaccine)


@hospital.route('/search vaccine', methods=['GET', 'POST'])
def search_vaccine():
    if not session.get('id'):
        return redirect('/signin')
    elif request.method == 'POST':
        name = request.form['searchItem']    
        if request.form['searchType'] == 'vaccineName' or request.form['searchType'] == 'default':        
            sql = f"select * from `Vaccine` where vaccineName REGEXP '{name}'"
        elif request.form['searchType'] == 'manufacturer':
            sql = f"select * from `Vaccine` where manufacturer REGEXP '{name}'"
        elif request.form['searchType'] == 'ageAdministered':
            sql = f"select * from `Vaccine` where ageAdministered REGEXP '{name}'"
        vaccines = _queryAllMembers(sql)
        return render_template('search/vaccines.html', vaccines=vaccines)
    return render_template('search/vaccines.html')


@hospital.route('/patient has allergy/<patientId>/<alergyName>')
def patient_has_allergy(patientId, alergyName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"insert into `Patient_has_Alergies`\
        (Patient_patientId, Alergies_alergyName)\
        values ('{patientId}', '{alergyName}')"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(sql)        
    mysql.connection.commit()
    return redirect(f'/detail patient/{patientId}')


@hospital.route('/patient add allergy/<patientId>/<fname>', methods=['POST', 'GET'])
def patient_add_allergy(patientId, fname):
    if not session.get('id'):
        return redirect('/signin')
    sql = "select * from `Alergies`"
    myallergies = _queryAllMembers(sql)
    allergies = []
    sql1 = f"select Alergies_alergyName from `Patient_has_Alergies` where Patient_patientId = '{patientId}'"
    patients = _queryAllMembers(sql1)
    mylist = list()
    for patient in patients:
        mylist.append(patient['Alergies_alergyName'])
    if request.method == 'POST':
        name = request.form['searchItem']  
        sql2 = f"select * from `Alergies` where alergyName REGEXP '{name}'"
        myallergies1 = _queryAllMembers(sql2)
        for myallergie1 in myallergies1:
            if myallergie1['alergyName'] not in mylist:
                allergies.append(myallergie1)
        return render_template('has/patient_add_allergy.html', patientId=patientId, fname=fname, allergies=allergies)
    for myallergy in myallergies:
        if myallergy['alergyName'] not in mylist:
            allergies.append(myallergy)
    return render_template('has/patient_add_allergy.html', patientId=patientId, fname=fname, allergies=allergies)


@hospital.route('/patient has vaccine/<patientId>/<vaccineName>')
def patient_has_vaccine(patientId, vaccineName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"insert into `Vaccine_has_Patient`\
        (Patient_patientId, Vaccine_vaccineName)\
        values ('{patientId}', '{vaccineName}')"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(sql)        
    mysql.connection.commit()
    return redirect(f'/detail patient/{patientId}')


@hospital.route('/patient add vaccine/<patientId>/<fname>', methods=['POST', 'GET'])
def patient_add_vaccine(patientId, fname):
    if not session.get('id'):
        return redirect('/signin')
    sql = "select * from `Vaccine`"
    myVaccines = _queryAllMembers(sql)
    vaccines = []
    sql1 = f"select Vaccine_vaccineName from `Vaccine_has_Patient` where Patient_patientId = '{patientId}'"
    patients = _queryAllMembers(sql1)
    mylist = list()
    for patient in patients:
        mylist.append(patient['Vaccine_vaccineName'])
    if request.method == 'POST':
        sql2 = f"select * from `Vaccine` where vaccineName REGEXP '{request.form['searchItem']}'"
        myVaccines1 = _queryAllMembers(sql2)
        for myVaccine1 in myVaccines1:
            if myVaccine1['vaccineName'] not in mylist:
                vaccines.append(myVaccine1)
        return render_template('has/patient_add_vaccine.html', patientId=patientId, fname=fname, vaccines=vaccines)
    for myvaccine in myVaccines:
        if myvaccine['vaccineName'] not in mylist:
            vaccines.append(myvaccine)
    return render_template('has/patient_add_vaccine.html', patientId=patientId, fname=fname, vaccines=vaccines)


@hospital.route('/disease has vaccine/<dieseaseName>/<vaccineName>')
def disease_has_vaccine(dieseaseName, vaccineName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"insert into `Diseases_has_Vaccine`\
        (Diseases_dieseaseName, Vaccine_vaccineName)\
        values('{dieseaseName}', '{vaccineName}')"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(sql)        
    mysql.connection.commit()
    return redirect(f'/detail disease/{dieseaseName}')


@hospital.route('/disease add vaccine/<dieseaseName>', methods=['POST', 'GET'])
def disease_add_vaccine(dieseaseName):
    if not session.get('id'):
        return redirect('/signin')
    sql = "select * from `Vaccine`"
    myVaccines = _queryAllMembers(sql)
    vaccines = []
    sql1 = f"select Vaccine_vaccineName from `Diseases_has_Vaccine` where Diseases_dieseaseName = '{dieseaseName}'"
    patients = _queryAllMembers(sql1)
    mylist = list()
    for patient in patients:
        mylist.append(patient['Vaccine_vaccineName'])
    if request.method == 'POST':
        sql2 = f"select * from `Vaccine` where vaccineName REGEXP '{request.form['searchItem']}'"
        myVaccines1 = _queryAllMembers(sql2)
        for myVaccine1 in myVaccines1:
            if myVaccine1['vaccineName'] not in mylist:
                vaccines.append(myVaccine1)
        return render_template('has/disease_add_vaccine.html', dieseaseName=dieseaseName, vaccines=vaccines)
    for myvaccine in myVaccines:
        if myvaccine['vaccineName'] not in mylist:
            vaccines.append(myvaccine)
    return render_template('has/disease_add_vaccine.html', dieseaseName=dieseaseName, vaccines=vaccines)


@hospital.route('/disease has drug/<dieseaseName>/<drugName>')
def disease_has_drug(dieseaseName, drugName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"insert into `Diseases_has_Drugs`\
        (Diseases_dieseaseName, Drugs_drugName)\
        values('{dieseaseName}', '{drugName}')"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(sql)        
    mysql.connection.commit()
    return redirect(f'/detail disease/{dieseaseName}')


@hospital.route('/disease add drug/<dieseaseName>', methods=['POST', 'GET'])
def disease_add_drug(dieseaseName):
    if not session.get('id'):
        return redirect('/signin')
    sql = "select * from `Drugs`"
    myVaccines = _queryAllMembers(sql)
    drugs = []
    sql1 = f"select Drugs_drugName from `Diseases_has_Drugs` where Diseases_dieseaseName = '{dieseaseName}'"
    patients = _queryAllMembers(sql1)
    mylist = list()
    for patient in patients:
        mylist.append(patient['Drugs_drugName'])
    if request.method == 'POST':
        sql2 = f"select * from `Drugs` where drugName REGEXP '{request.form['searchItem']}'"
        mydrugs = _queryAllMembers(sql2)
        for mydrug in mydrugs:
            if mydrug['drugName'] not in mylist:
                drugs.append(mydrug)
        return render_template('has/disease_add_drug.html', dieseaseName=dieseaseName, drugs=drugs)
    for myvaccine in myVaccines:
        if myvaccine['drugName'] not in mylist:
            drugs.append(myvaccine)
    return render_template('has/disease_add_drug.html', dieseaseName=dieseaseName, drugs=drugs)


@hospital.route('/logout')
def logout():
    if not session.get('id'):
        return redirect('/signin')
    session['id'] = None 
    return redirect('/')


@hospital.route('/employee details')
def employee_details():
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Employee` where id = '{session.get('id')}'"
    employee = _queryOneMember(sql)
    sql1 = f"select * from `Doctor` where Employee_id = '{session.get('id')}'"
    specialises = _queryAllMembers(sql1)
    stations = []
    for special in specialises:
        sql2 = f"select * from `Specialisation` where specialisation='{special['Specialisation_specialisation']}'"
        stations.append(_queryOneMember(sql2))
    return render_template('detail/employees.html', employee=employee, stations=stations)


@hospital.route('/employee edit', methods=['POST', 'GET'])
def employee_edit():
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Employee` where id = '{session.get('id')}'"
    employee = _queryOneMember(sql)
    if request.method == 'POST':
        sql1 = f"update `Employee` set \
            fname='{request.form['fname']}', lname='{request.form['lname']}', email='{request.form['email']}', telephone='{request.form['telephone']}', \
            address='{request.form['address']}', city='{request.form['city']}', dateEmployed='{request.form['dateEmployed']}', rank='{request.form['rank']}'\
            where id='{session.get('id')}'"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql1)        
        mysql.connection.commit()
        return redirect('/employee details')
    return render_template('edit/employees.html', employee=employee)


@hospital.route('/employee password', methods=['GET', 'POST'])
def employee_password():
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Employee` where id = '{session.get('id')}'"
    employee = _queryOneMember(sql)
    if request.method == 'POST':
        myPassword = (employee['password'] == request.form['password'])
        myPassword1 = (request.form['password1'] == request.form['password2'])
        if myPassword:
            if myPassword1:
                sql1 = f"update `Employee` set \
                    password = '{request.form['password1']}' where id = '{session.get('id')}'"
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(sql1)        
                mysql.connection.commit()
                return redirect('/employee details')
            else:
                return render_template('edit/employee_password.html', employee=employee, myPassword=myPassword, myPassword1=myPassword1)
        else:
            if myPassword1:
                return render_template('edit/employee_password.html', employee=employee, myPassword=myPassword, myPassword1=myPassword1)
            else:
                return render_template('edit/employee_password.html', employee=employee, myPassword=myPassword, myPassword1=myPassword1)
    return render_template('edit/employee_password.html', employee=employee)


@hospital.route("/employee specialisation", methods=["GET", "POST"])
def employee_specialisation():
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Employee` where id = '{session.get('id')}'"
    employee = _queryOneMember(sql)
    sql1 = f"select * from `Specialisation`"
    specs = _queryAllMembers(sql1)
    sql2 = f"select Specialisation_specialisation from `Doctor` where Employee_id = '{session.get('id')}'"
    mylist1 = _queryAllMembers(sql2)
    mylist = []
    specialisations = []
    for i in mylist1:
        mylist.append(i['Specialisation_specialisation'])
    for spec in specs:
        if spec['specialisation'] not in mylist:
            specialisations.append(spec)
    return render_template('has/doctor.html', employee=employee, specialisations=specialisations)


@hospital.route('/employee specialise/<specialisation>')
def employee_specialise(specialisation):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"insert into `Doctor` (Employee_id, Specialisation_specialisation) \
        values ('{session.get('id')}', '{specialisation}')"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(sql)        
    mysql.connection.commit()
    return redirect('/employee details')


@hospital.route('/register treatment', methods=['POST', 'GET'])
def register_treatment():
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select Specialisation_specialisation from `Doctor` where Employee_id = '{session.get('id')}'"
    specialisation = _queryAllMembers(sql)
    sql1 = f"select patientId from `Patient`"
    patients = _queryAllMembers(sql1)
    if request.method == 'POST':
        date  = datetime.ctime(datetime.now())
        sql2 = f"insert into `Treatment` \
            (Patient_patientId, Doctor_Employee_id, Doctor_Specialisation_specialisation, date, weight, doctorsNotes, reasonForVisit, recomendations, diagnosis) \
            values('{request.form['patientId']}', '{session.get('id')}', '{request.form['specialisation']}', '{date}', \
            '{request.form['weight']}', '{request.form['doctor-notes']}', '{request.form['reason-for-visit']}', ' ', ' ')"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql2)        
        mysql.connection.commit()
        sql3 = f"select * from `Treatment` where Patient_patientId='{request.form['patientId']}' and date='{date}' and  Doctor_Employee_id='{session.get('id')}'"
        treat = _queryOneMember(sql3)
        return redirect(f"success treatment/{treat['id']}")
    return render_template('treatment/register.html', specialisation=specialisation, patients=patients)


@hospital.route('/success treatment/<id>', methods=['POST', 'GET'])
def success_treatment(id):
    sql = f"select * from `Treatment` where id = '{id}'"
    treatment = _queryOneMember(sql)
    sql1 = f"select * from `Patient` where patientId='{id}'"
    patient = _queryOneMember(sql1)
    sql2 = f"select * from `Employee` where id='{session.get('id')}'"
    employee = _queryOneMember(sql2)
    sql3 = f"select * from `Diseases_has_Treatment` where Treatment_id='{id}'"
    diseases = _queryAllMembers(sql3)
    sql4 = f"select * from `Treatment_has_Drugs` where Treatment_id='{id}'"
    drugs = _queryAllMembers(sql4)
    reason_for_visit = treatment['reasonForVisit'].split('\n')
    doctors_notes = treatment['doctorsNotes'].split('\n')
    recommendations = treatment['recomendations'].split('\n')
    diagnosis = treatment['diagnosis'].split('\n')
    return render_template('treatment/success.html', id=id, treatment=treatment, patient=patient, employee=employee, reason_for_visit=reason_for_visit,
        doctors_notes=doctors_notes, recommendations=recommendations, diagnosis=diagnosis, diseases=diseases, drugs=drugs)


@hospital.route('/all treatments')
def all_treatment():
    sql = 'select * from `Treatment`'
    sql1 = 'select * from `Patient`'
    sql2 = 'select * from `Employee`'
    treatment = _queryAllMembers(sql)
    patients = _queryAllMembers(sql1)
    employees = _queryAllMembers(sql2)
    for treat in treatment:
        for patient in patients:
            if treat['Patient_patientId'] == patient['patientId']:
                treat.update({'patientFname': patient['fname']})
                break
        for employee in employees:
            if treat['Doctor_Employee_id'] == employee['id']:
                treat.update({'employeeFname': employee['fname']})
    return render_template('all/treatment.html', treatment=treatment)


@hospital.route('/employee diagnise/<treatId>/<fname>', methods=['GET', 'POST'])
def employee_diagnise(treatId, fname):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Treatment` where id='{treatId}'"
    treatment = _queryOneMember(sql)
    if request.method == 'POST':
        sql1 = f"update `Treatment` set \
            recomendations='{request.form['recommendations']}', diagnosis='{request.form['diagnosis']}' where id={treatId}"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql1)        
        mysql.connection.commit()
        return redirect(f"/success treatment/{treatId}")
    return render_template('treatment/diagnise.html', treatId=treatId, fname=fname, treatment=treatment)


@hospital.route('/employee prescription/<treatId>/<fname>', methods=['GET', 'POST'])
def employee_prescription(treatId, fname):
    if not session.get('id'):
        return redirect('/signin')
    seldrugs = []
    sql1 = f"select * from `Treatment_has_Drugs` where Treatment_id='{treatId}'"
    mydrugs = _queryAllMembers(sql1)
    sql2 = "select * from `Drugs`"
    drugs1 = _queryAllMembers(sql2)
    mylist = []
    drugs = []
    for mydrug in mydrugs:
        mylist.append(mydrug['Drugs_drugName'])
    for drug1 in drugs1:
        if drug1['drugName'] in mylist:
            seldrugs.append(drug1)
    for seldrug in seldrugs:
        for mydrug1 in mydrugs:
            if mydrug1['Drugs_drugName'] in seldrug['drugName']:
                seldrug.update({"prescription": mydrug1['prescription']})
    if request.method == 'POST':
        name = request.form['searchItem']    
        if request.form['searchType'] == 'drugName' or request.form['searchType'] == 'default':        
            sql = f"select * from `Drugs` where drugName REGEXP '{name}'"
        elif request.form['searchType'] == 'drugManufacturer':
            sql = f"select * from `Drugs` where drugManufacturer REGEXP '{name}'"
        drugs2 = _queryAllMembers(sql)
        for drug3 in drugs2:
            if drug3['drugName'] not in mylist:
                drugs.append(drug3)
        return render_template('treatment/prescription.html', treatId=treatId, fname=fname, drugs=drugs, seldrugs=seldrugs)
    for drug2 in drugs1:
        if drug2['drugName'] not in mylist:
            drugs.append(drug2)
    return render_template('treatment/prescription.html', treatId=treatId, fname=fname, drugs=drugs, seldrugs=seldrugs)


@hospital.route('/treatment add drug/<treatId>/<fname>/<drugName>')
def treatment_add_drug(treatId, fname, drugName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Treatment` where id='{treatId}'"
    treatment = _queryOneMember(sql)
    sql1 = f"insert into `Treatment_has_Drugs` \
        (Treatment_id, Treatment_Doctor_Employee_id, Treatment_Doctor_Specialisation_specialisation, Treatment_Patient_patientId, \
        Drugs_drugName, prescription)\
        values ('{treatId}', '{treatment['Doctor_Employee_id']}', '{treatment['Doctor_Specialisation_specialisation']}', '{treatment['Patient_patientId']}', \
        '{drugName}', ' ')"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(sql1)        
    mysql.connection.commit()
    return redirect(f"/prescribe drug/{treatId}/{fname}/{drugName}")


@hospital.route('/treatment add disease/<treatId>/<fname>/<diseaseName>')
def treatment_add_disease(treatId, fname, diseaseName):
    if not session.get('id'):
        return redirect('/signin')
    sql = f"select * from `Treatment` where id='{treatId}'"
    treatment = _queryOneMember(sql)
    sql3 = f"insert into `Diseases_has_Treatment` \
        (Treatment_id, Treatment_Doctor_Employee_id, Treatment_Doctor_Specialisation_specialisation, Treatment_Patient_patientId, Diseases_dieseaseName) \
        values ('{treatId}', '{treatment['Doctor_Employee_id']}', '{treatment['Doctor_Specialisation_specialisation']}', '{treatment['Patient_patientId']}', \
        '{diseaseName}')"
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(sql3)        
    mysql.connection.commit()
    sql1 = "select * from `Diseases`"
    diseases1 = _queryAllMembers(sql1)
    sql2 = f"select * from `Diseases_has_Treatment` where Treatment_id='{treatId}'"
    mydiseases = _queryAllMembers(sql2)
    seldiseases = []
    mylist = []
    diseases = []
    for mydisease in mydiseases:
        mylist.append(mydisease['Diseases_dieseaseName'])
    for disease2 in diseases1:
        if disease2['dieseaseName'] in mylist:
            seldiseases.append(disease2)
        else:
            diseases.append(disease2)
    return render_template('has/treatment_has_disease.html', treatId=treatId, fname=fname, diseases=diseases, seldiseases=seldiseases)


@hospital.route('/treatment has disease/<treatId>/<fname>', methods=['GET', 'POST'])
def treatment_has_disease(treatId, fname):
    if not session.get('id'):
        return redirect('/signin')
    seldiseases = []
    sql2 = f"select * from `Diseases_has_Treatment` where Treatment_id='{treatId}'"
    mydiseases = _queryAllMembers(sql2)
    sql3 = "select * from `Diseases`"
    diseases1 = _queryAllMembers(sql3)
    mylist = []
    for mydisease in mydiseases:
        mylist.append(mydisease['Diseases_dieseaseName'])
    for disease1 in diseases1:
        if disease1['dieseaseName'] in mylist:
            seldiseases.append(disease1)
    if request.method == 'POST':
        name = request.form['searchItem']
        if request.form['searchType'] == 'dieseaseName' or request.form['searchType'] == 'default':
            sql = f"select * from `Diseases` where dieseaseName REGEXP '{name}'"
        elif request.form['searchType'] == 'typeofCause':
            sql = f"select * from `Diseases` where typeofCause REGEXP '{name}'"
        elif request.form['searchType'] == 'nameofCause':
            sql = f"select * from `Diseases` where nameofCause REGEXP '{name}'"
        diseases1 = _queryAllMembers(sql)
        diseases = []
        for disease2 in diseases1:
            if disease2['dieseaseName'] not in mylist:
                diseases.append(disease2)
        return render_template('has/treatment_has_disease.html', treatId=treatId, fname=fname, diseases=diseases, seldiseases=seldiseases)
    sql1 = "select * from `Diseases`"
    diseases1 = _queryAllMembers(sql1)
    diseases = []
    for disease2 in diseases1:
        if disease2['dieseaseName'] not in mylist:
            diseases.append(disease2)
    return render_template('has/treatment_has_disease.html', treatId=treatId, fname=fname, diseases=diseases, seldiseases=seldiseases)


@hospital.route('/prescribe drug/<treatId>/<fname>/<drugName>', methods=['POST', 'GET'])
def prescribe_drug(treatId, fname, drugName):
    if not session.get('id'):
        return redirect('/signin')
    if request.method == 'POST':
        sql = f"update `Treatment_has_Drugs` set \
            prescription='{request.form['prescribe']}' where Treatment_id='{treatId}' and Drugs_drugName='{drugName}'"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)        
        mysql.connection.commit()
        return redirect(f"/employee prescription/{treatId}/{fname}")
    return render_template('has/prescibe.html', treatId=treatId, fname=fname, drugName=drugName)


@hospital.route('/test/<text>')
def test(text):
    return text
