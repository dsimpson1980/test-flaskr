# all the imports
import pandas as pd
import numpy as np
import sqlalchemy as sa
from config import *

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
from contextlib import closing

from wtforms import Form, validators, TextField, BooleanField
from wtforms.fields.html5 import DateField
import psycopg2

app = Flask(__name__)
app.config.from_object(__name__)
# postgres config
db = SQLAlchemy(app)

#class Customer(db.Model):
#    customer_id = db.Column(db.Integer, primary_key = True)
#    name = db.Column(db.String(64), index = True, unique = True)
#    market_id = db.Column(db.Integer, index = True, unique = True)
#
#class Premium(db.Model):
#    premium_id = db.Column(db.Integer, primary_key = True)
#    customer_id = db.Column(db.Integer, index = True)
#    run_id = db.Column(db.Integer, index = True)
#    valuation_date = db.Column(db.DateTime, index = True)
#    contract_start_date_utc = db.Column(db.DateTime, index = True)
#    contract_end_date_utc = db.Column(db.DateTime, index = True)
#    premium = db.Column(db.Float, index = True)
#
#class Parameter(db.Model):
#    run_id = db.Column(db.Integer, primary_key = True)
#    market_id = db.Column(db.Integer, index = True)
#    parameters = db.Column(db.Integer, index = True)
#    db_upload_date = db.Column(db.DateTime, index = True)

engine = sa.create_engine(SQLALCHEMY_DATABASE_URI, convert_unicode=True)

meta = sa.MetaData(bind=engine, schema='retail')
schema = 'retail'
meta.reflect(bind=engine, schema=schema)
db = SQLAlchemy(app)

class Market(db.Model):
     __tablename__ = 'markets'
     metadata = meta

class Customer(db.Model):
    __tablename__ = 'customers'
    metadata = meta

class Premium(db.Model):
     __tablename__ = 'premiums'
     metadata = meta

class CustomerDemand(db.Model):
     __tablename__ = 'customer_demand'
     metadata = meta

class Parameter(db.Model):
     __tablename__ = 'run_parameters'
     metadata = meta

def connect_db():
    import urlparse

    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(SQLALCHEMY_DATABASE_URI)
    return psycopg2.connect(database=url.path[1:],
                            user=url.username,
                            password=url.password,
                            host=url.hostname,
                            port=url.port)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
@app.route('/index/<int:page>')
def show_customers(page=1):
    customers = Customer.query.paginate(page, CUSTOMERS_PER_PAGE, False)
    #customers = CustomerWithMarket.query.paginate(page, CUSTOMERS_PER_PAGE, False)
    return render_template('show_customers.html', customers=customers)

@app.route('/add_customer', methods=['POST'])
def add_customer():
    from StringIO import StringIO
    if not session.get('logged_in'):
        abort(401)
    demand = generate_random_customer_data()
    image64 = generate_customer_demand_image(demand)

    new_customer = Customer(name=request.form['name'],
                            market_id=1,
                            image64=image64)
    db.session.add(new_customer)
    db.session.commit()
    ids = np.array(range(len(demand)))
    ids.fill(new_customer.customer_id)
    demand_data = pd.DataFrame({'customer_id': 1,
                                'datetime': '01-Sep-13',
                                'value': 1})
    #demand_buffer = StringIO()
    #demand_data.to_csv(demand_buffer, header=False, index=False)
    #demand_buffer.seek(0)
    #cur = engine.raw_connection().cursor()
    #cur.copy_from(demand_buffer, 'retail.customer_demand', sep=',')
    #cur.connection.commit()
    # add push to db demand table here
    flash('New customer was successfully added')
    return redirect(url_for('show_customers'))

@app.route('/generate_customer_premium/<int:customer_id>', methods=['GET', 'POST'])
def generate_customer_premium(customer_id):
    from datetime import datetime
    #from dateutil.relativedelta import relativedelta
    if not session.get('logged_in'):
        abort(401)
    form = premium_parameters_form(request.form)
    if request.method == "POST" and form.validate():
        contract_end = []
        if form.contract12:
            #contract_end.append(form.contract_start.data + relativedelta(months=12+1, days=-1))
            contract_end.append(form.contract_start.data)
        #if form.contract24:
        #    contract_end.append(form.contract_start + relativedelta(months=12*2+1, days=-1))
        #if form.contract36:
        #    contract_end.append(form.contract_start + relativedelta(months=12*3+1, days=-1))
        contract_start = [form.contract_start for x in range(len(contract_end))]
        valuation_date = datetime.today()
        customer = Customer.query.filter(Customer.customer_id==customer_id).one()
        #customer = CustomerWithMarket.query.filter(Customer.customer_id==customer_id).one()
        parameters = fetch_run_parameters(customer.market_id)
        run_id = parameters.run_id
        premium = np.random.rand()
        new_premium = Premium(customer_id=customer_id,
                              run_id=run_id,
                              valuation_date=valuation_date,
                              contract_start_date_utc=form.contract_start.data,
                              contract_end_date_utc=datetime(*(contract_end[0].timetuple()[:6])),
                              premium=premium)
        db.session.add(new_premium)
        db.session.commit()
        flash('Premium has been queued for generation')
        return display_customer_premiums(customer_id)
    customer = Customer.query.filter(Customer.customer_id==customer_id).one()
    return render_template('generate_customer_premium.html',
                           form=form,
                           customer=customer)

class premium_parameters_form(Form):
    from datetime import datetime
    #from dateutil.relativedelta import relativedelta
    #default_start = datetime.today() + relativedelta(months=1, day=1)
    default_start = datetime.today()
    contract_start = DateField(label="contract_start",
                               default=default_start)
    #choices = [(None, '0')] + [(x, str(x)) for x in range(1,36)]
    #contract_adhoc = ChoiceField(label='ad hoc months', choices=choices, required=False)
    contract12 = BooleanField(label="12 months", default=True)
    contract24 = BooleanField(label="24 months")
    contract36 = BooleanField(label="36 months")
    email = TextField(label='Email',
                      default='mapdes@gmail.com',
                      validators=[validators.Email(message='Invalid email address')])

@app.route('/display_customer_premiums/<int:customer_id>/<int:page>')
@app.route('/display_customer_premiums/<int:customer_id>')
def display_customer_premiums(customer_id, page=1):
    if not session.get('logged_in'):
        abort(401)
    #customer = CustomerWithMarket.query.filter(Customer.customer_id==customer_id).one()
    customer = Customer.query.filter(Customer.customer_id==customer_id).one()
    premiums = Premium.query.filter(Premium.customer_id==customer_id)
    premiums = premiums.paginate(page, PREMIUMS_PER_PAGE, False)
    return render_template('display_customer_premiums.html',
                           customer=customer,
                           premiums=premiums)

@app.route('/display_customer/<int:customer_id>/<int:page>')
@app.route('/display_customer/<int:customer_id>')
def display_customer(customer_id, page=1):
    if not session.get('logged_in'):
        abort(401)
    #customer = CustomerWithMarket.query.filter(Customer.customer_id==customer_id).one()
    #customer_demand = CustomerDemand.query.filter(CustomerDemand.customer_id==customer_id)
    #customer_demand = customer_demand.paginate(page, DEMAND_ITEMS_PER_PAGE, False)
    customer = Customer.query.filter(Customer.customer_id==customer_id).one()
    customer_demand = 0
    return render_template('display_customer.html',
                           customer_demand=customer_demand,
                           customer=customer)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_customers'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

def generate_random_customer_data():
    """Generates some random customer data

    Dependencies
    ------------

    pandas
    numpy

    Inputs
    ------

    None

    Outputs
    -------

    demand - pd.TimeSeries
        randomly generated DataFrame covering 30 days in Sep-13 at daily freq

    """
    start_date = '01-Sep-13'
    end_date = '30-Sep-13'
    dates = pd.date_range(start_date, end_date, freq='D')
    values = np.random.rand(len(dates))
    demand = pd.TimeSeries(values, dates)
    return demand

def generate_customer_demand_image(demand):
    """Creates a plot and saves it to a string buffer

    Dependencies
    ------------
    matplotlib.pyplot
    StringIO.StringIO
    Base64

    Inputs
    ------
    demand: pandas.TimeSeries
        The historical demand for the customer

    Outputs
    -------

    image64: StringIO
        The string buffer containing the image plot


    """
    import matplotlib.pyplot as plt
    from StringIO import StringIO
    import base64

    # Extract the timeseries part from the demand dataframe

    # Plot the historical demand
    demand.plot()
    plt.xlabel('date')
    plt.ylabel('demand (kwh')
    plt.title('Historical Demand')
    plt.grid(True)

    # Store image in a string buffer and encode in base64
    buffer = StringIO()
    plt.savefig(buffer)
    plt.close()
    buffer.getvalue()
    _historical_demand_image64 = base64.b64encode(buffer.getvalue())
    return _historical_demand_image64

def fetch_run_parameters(market_id):
    parameters = Parameter.query.filter(Parameter.market_id==market_id).order_by(Parameter.db_upload_date).first()
    return parameters

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
