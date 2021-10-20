import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

def connect_to_db():
    conn = sqlite3.connect('ceremonial-api.db')
    return conn

def create_inv_table():
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    item_id INTEGER PRIMARY KEY NOT NULL,
                    name TEXT NOT NULL,
                    size TEXT NOT NULL,
                    price REAL NOT NULL,
                    qty INTEGER NOT NULL,
                    source TEXT NOT NULL
                );
            '''
        )
        conn.commit()
        print('inventory table created successfully')
    except Exception as e:
        print('inventory table creation failed -- check connection')
        print(e)
    finally:
        conn.close()

def reset_inv():
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute('''
                DROP TABLE inventory;
            ''')
        conn.commit()
        print('inventory table truncated successfully')
        create_inv_table()
    except:
        print('could not reset inventory')

def create_hist_table():
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute('''
                CREATE TABLE IF NOT EXISTS purchases (
                    purchase_id INTEGER PRIMARY KEY NOT NULL,
                    brother TEXT NOT NULL,
                    item_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    qty_prior INTEGER NOT NULL,
                    qty_remain INTEGER NOT NULL
                );
            ''')
        conn.commit()
        print('purchase history table created successfully')
    except Exception as e:
        print('purchase table creation failed -- check connection')
        print(e)
    finally:
        conn.close()

def add_item_to_inventory(item):
    # print(item)
    inserted_item = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO inventory (name, price, size, qty, source) 
            VALUES (?, ?, ?, ?, ?)''',
            (item['name'], item['price'], item['size'], item['qty'], item['source'])
        )
        conn.commit()
        inserted_item = get_item_by_id(cur.lastrowid)
        inserted_item['status'] = 'inserted successfully'
    except Exception as e:
        inserted_item['status'] = 'failure to insert: ' + str(e)
        print('insertion failed', e)
        conn.rollback()
    finally:
        conn.close()
    return inserted_item
    
def get_all_items():
    items = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM inventory')
        rows = cur.fetchall()
        # convert row objects to dictionary
        for row in rows:
            item = {}
            item['item_id'] = row['item_id']
            item['name'] = row['name']
            item['price'] = row['price']
            item['size'] = row['size']
            item['qty'] = row['qty']
            item['source'] = row['source']
            items.append(item)
    except:
        items = []
    return items

def get_item_by_id(item_id):
    item = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM inventory WHERE item_id = ?', (item_id,))
        row = cur.fetchone()
        # convert row object to dictionary
        item['item_id'] = row['item_id']
        item['name'] = row['name']
        item['price'] = row['price']
        item['size'] = row['size']
        item['qty'] = row['qty']
        item['source'] = row['source']
    except:
        item = {}
    return item

def update_item(item):
    updated_item = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute('''UPDATE inventory SET name = ?, price = ?, size = ?, qty = ?, source = ?
                     WHERE item_id =?''',  
                     (item['name'], item['price'], item['size'], item['qty'], item['source'], item['item_id']))
        conn.commit()

        #return the item
        updated_item = get_item_by_id(item['item_id'])
        updated_item['status'] = 'updated successfully'

    except Exception as e:
        print(e)
        updated_item['status'] = 'failure to update: ' + str(e)
        conn.rollback()

    finally:
        conn.close()

    return updated_item

def add_hist_record(item):
    inserted_rec = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO purchases (brother, item_id, item_name, price, qty_prior, qty_remain) 
            VALUES (?, ?, ?, ?, ?, ?)''',
            (item['brother'], item['item_id'], item['item_name'], item['price'], item['qty_prior'], item['qty_remain'])
        )
        conn.commit()
        inserted_rec = get_item_by_id(cur.lastrowid)
        inserted_rec['status'] = 'inserted successfully'
    except Exception as e:
        inserted_rec['status'] = 'failure to insert: ' + str(e)
        print('insertion failed', e)
        conn.rollback()
    finally:
        conn.close()
    return inserted_rec

def get_hist_records():
    return {}

# flask starts
app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

# HOME PAGE
@app.route('/ceremonial-api/items', methods=['GET'])
def ceremonial_api_get_items():
    return jsonify(get_all_items())

# GET ITEM BY item_id
@app.route('/ceremonial-api/items/view/<item_id>', methods=['GET'])
def ceremonial_api_get_item(item_id):
    return jsonify(get_item_by_id(item_id))

# ADD NEW ITEM ENTRY
@app.route('/ceremonial-api/items/add', methods=['POST'])
def ceremonial_api_add_item_to_inventory():
    item = request.json
    print(item)
    return jsonify(add_item_to_inventory(item))

# UPDATE ITEM
@app.route('/ceremonial-api/items/update', methods=['PUT'])
def ceremonial_api_update_item():
    item = request.json
    return jsonify(update_item(item))

@app.route('/ceremonial-api/hist', methods=['GET'])
def ceremonial_api_get_hist_records():
    return jsonify(get_hist_records())

@app.route('/ceremonial-api/hist/add', methods=['POST'])
def ceremonial_api_add_hist_record():
    # item = request.form.to_dict() # NOTE POSTMAN ONLY
    item = request.json # NOTE PROD
    print(item)
    return jsonify(add_hist_record(item))

if __name__ == '__main__':
    # reset_inv()
    # create_hist_table()
    app.run('0.0.0.0', debug=True)