import os

from flask import Flask, render_template, request, redirect
import flask_cors
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = 'sqlite:///{}'.format(os.path.join(project_dir, 'ceremonial.db'))


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Item(db.Model):
    name = db.Column(db.String(200), unique=True, nullable=False, primary_key=True)

    def __repr__(self):
        return "<Name: {}>".format(self.name)

@app.route('/', methods=['GET', 'POST'])
@flask_cors.cross_origin()
def home():
    items = None
    if request.form:
        try:
            name = Item(name=request.form.get('item'))
            db.session.add(name)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print('failed to add item')
            print(e)
        finally:
            db.session.close()
    items = Item.query.all()
    return render_template('home.html', items=items)

@app.route("/update", methods=["POST"])
@flask_cors.cross_origin()
def update():
    try:
        new_name = request.form.get("new_name")
        old_name = request.form.get("old_name")
        item = Item.query.filter_by(name=old_name).first()
        item.name = new_name
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f'failed to update item {old_name}')
        print(e)
    finally:
        db.session.close()
    return redirect("/")

@app.route("/delete", methods=["POST"])
@flask_cors.cross_origin()
def delete():
    del_name = request.form.get("del_name")
    item = Item.query.filter_by(name=del_name).first()
    db.session.delete(item)
    db.session.commit()
    return redirect("/")

@app.after_request
def after(response):
    # print(response.status)
    # print(response.headers)
    # print('RESPONSE HTML:')
    # data = response.get_data().decode('utf-8')
    # data = data.strip('\t')
    # for line in data.split('\n'):
    #     print(line)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)