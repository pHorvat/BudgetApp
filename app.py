from datetime import datetime
import requests
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
db = SQLAlchemy(app)

app.app_context().push()
url = "https://api.hnb.hr/tecajn-eur/v3"

response = requests.get(url)
if response.status_code == 200:
    tecaj = response.json()
else:
    print(f"Request failed with status code: {response.status_code}")

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float(precision=2), nullable=False)
    date_crated = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.Text, nullable=False)
    user_name = db.Column(db.Text, nullable=False)
    currency = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return '<Transaction %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        cat=request.form['expenseCategory']
        if cat=='all':
            transactions = Budget.query.order_by(Budget.date_crated).all()
        else:
            transactions = Budget.query.filter(Budget.type == cat).order_by(Budget.date_crated)
        total=0
        ex_rate=0
        for trs in transactions:
            for item in tecaj:
                if trs.currency=="EUR":
                    ex_rate=1
                    break
                if item["valuta"] == trs.currency:
                    ex_rate = item["srednji_tecaj"]
                    ex_rate=ex_rate.replace(",",".")
                    break
            total=total+(trs.amount/float(ex_rate))
            total = round(total, 2)
        return render_template('index.html', transaction=transactions, total=total)


    else:
        transactions = Budget.query.order_by(Budget.date_crated).all()
        total=0
        ex_rate=0
        for trs in transactions:
            for item in tecaj:
                if trs.currency=="EUR":
                    ex_rate=1
                    break
                if item["valuta"] == trs.currency:
                    ex_rate = item["srednji_tecaj"]
                    ex_rate=ex_rate.replace(",",".")
                    break
            total=total+(trs.amount/float(ex_rate))
            total =round(total, 2)
        return render_template('index.html', transaction=transactions, total=total)


@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    trDel=Budget.query.get_or_404(id)
    try:
        db.session.delete(trDel)
        db.session.commit()
        return redirect('/')
    except:
        return 'Error deleting transaction'

@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        amount = request.form['amount']
        name = request.form['name']
        category = request.form['expenseCategory']
        currency = request.form['currency']
        date = request.form['date']
        date = datetime.strptime(date, '%Y-%m-%d')
        description = request.form['description']

        newTransaction = Budget(
            amount=amount,
            type=category,
            date_crated=date,
            user_name=name,
            currency=currency,
            description=description,
        )
        try:
            db.session.add(newTransaction)
            db.session.commit()
            return redirect('/')
        except:
            return 'Error adding transaction'
    else:
        return render_template('add.html')

if __name__ == '__main__':
    app.run()
