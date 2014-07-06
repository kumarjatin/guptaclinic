#@requires_login()
import json
def check_add_form(form):
    """
    Checks if the fields are in good shape
    """
    name = form.vars.name
    mobile = form.vars.mobile
    age = form.vars.age
    dups = db(db.patients.name == name)(db.patients.mobile == mobile).select()
    if any(dups):
        form.errors.name = 'Record already exists. PID: %s' % (dups[0]['id'])

def add_patient():
    """
    Adds new patient
    """
    mark_required(db.patients)
    form = SQLFORM(db.patients)
    if request.vars.name:
        form.vars.name = request.vars.name
    if form.process(onvalidation=check_add_form).accepted:
        pid = db(db.patients.name == form.vars.name)(db.patients.age == form.vars.age)(db.patients.mobile == form.vars.mobile).select()
        session.flash = '%s added. ID: %s' % (form.vars.name, pid[0]['id'])
    else:
        session.flash = 'Form has errors'
    return dict(form=form)

def edit_patient():
    """
    Update an existing patient
    """
    mark_required(db.patients)
    pid = request.args(0)
    record = db.patients(pid)
    form = SQLFORM(db.patients, record, submit_button='Update', deletable=True)
    if form.process(onvalidation=check_add_form).accepted:
        pid = db(db.patients.name == form.vars.name)(db.patients.age == form.vars.age)(db.patients.mobile == form.vars.mobile).select()
        if not pid:
            session.flash = '%s deleted' % (form.vars.name)
            redirect(URL('search'))
        else:
            session.flash = '%s updated. ID: %s' % (form.vars.name, pid[0]['id'])
    else:
        session.flash = 'Form has errors'
    return dict(form=form, pid=pid)

def search():
    """
    Dummy search form
    """
    session.flash = 'Fill in name or mobile number'
    return dict()

def search_patient():
    """
    Search patient form
    """
    pid = request.args[0] if any(request.args) else None
    if not pid:
        return None
    pid = int(pid)
    records = db(db.visits.pid == pid).select(limitby=(0,15), orderby=~db.visits.id)
    jsonResults = []
    order = ['id', 'date', 'diagnosis', 'treatment', 'remarks']
    for record in records:
        info = {'id':record['id'], 'date':str(record['currentdate']),
                'diagnosis':record['diagnosis'], 'treatment':record['treatment'],
                'remarks':record['remarks']}
        jsonResults.append(info)
    if any(jsonResults):
        return jsonToTable(jsonResults, order)
    else:
        return None

def add_visit():
    """
    Adds new treatment details for a patient visit
    """
    mark_required(db.visits)
    details = {}
    records = []
    if request.vars.pid:
        db.visits.pid.readable = False
        db.visits.pid.writable = False
        details = db(db.patients.id == request.vars.pid).select()[0]
        records = db(db.visits.pid == request.vars.pid).select(limitby=(0,15), orderby=~db.visits.id)
    form = SQLFORM(db.visits)
    if request.vars.pid:
        form.vars.pid = request.vars.pid
    if form.process().accepted:
        session.flash = 'Visit added for %s' % form.vars.name
    else:
        session.flash = 'Form has errors'
    return dict(form=form,details=details,records=records)

def search_patient_name_mobile():
    """
    Creates search form for looking into patients database
    """
    partialstr = '%' + request.vars.term + '%'
    results = db( db.patients.name.like(partialstr) | db.patients.mobile.like(partialstr) ).select(limitby=(0,15))
    jsonResults = []
    for result in results:
        label = '#%d. %s (%s, %s)' % (result['id'], result['name'], result['mobile'], result['age'])
        info = {'label':label, 'value':label}
        jsonResults.append(info)
    return json.dumps(jsonResults)

def aboutme():
    """
    Render about me page
    """
    response.flash = T("Dr. Sachin's clinic")
    return dict()
