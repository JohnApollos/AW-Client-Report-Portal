from flask import Flask, request, jsonify, send_from_directory
import os
import database as db
import pdf_generator
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='')

if os.environ.get('VERCEL'):
    REPORTS_DIR = '/tmp/reports'
else:
    REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

db.init_db()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/clients', methods=['GET'])
def get_clients():
    clients = db.get_clients()
    return jsonify(clients)

@app.route('/api/clients', methods=['POST'])
def create_client():
    data = request.json
    client_id = db.create_client(data)
    return jsonify({"id": client_id, "message": "Client created successfully"}), 201

@app.route('/api/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    client = db.get_client(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(client)

@app.route('/api/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    data = request.json
    db.update_client(client_id, data)
    return jsonify({"message": "Client updated successfully"})

def calculate_age(dob_str):
    try:
        if not dob_str: return ''
        dob = datetime.strptime(dob_str, '%Y-%m-%d')
        today = datetime.now()
        return str(today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day)))
    except:
        return ''

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    data = request.json
    client_id = data.get('client_id')
    date_str = data.get('date')
    balances = data.get('balances', []) 
    
    client = db.get_client(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    db.update_account_balances(client_id, balances)
    client = db.get_client(client_id)
    
    inflow = client.get('salary_client1', 0) + client.get('salary_client2', 0)
    outflow = client.get('expense_budget', 0)
    excess = max(0, inflow - outflow)
    
    pr_target = (6 * client.get('expense_budget', 0)) + client.get('insurance_deductibles', 0)
    
    client['age'] = calculate_age(client.get('dob'))
    client['spouse_age'] = calculate_age(client.get('spouse_dob'))
    
    ret_client1 = 0
    ret_client2 = 0
    non_ret = 0
    trust_val = 0
    liabilities = 0
    
    for acc in client.get('accounts', []):
        bal = acc.get('last_known_balance', 0)
        cat = acc.get('category')
        owner = acc.get('owner')
        
        if cat == 'retirement':
            if owner == 'client1':
                ret_client1 += bal
            elif owner == 'client2':
                ret_client2 += bal
        elif cat == 'non_retirement':
            non_ret += bal
        elif cat == 'trust':
            trust_val += bal
        elif cat == 'liability':
            liabilities += bal
            
    grand_total = ret_client1 + ret_client2 + non_ret + trust_val
    
    report_data = {
        "client": client,
        "calculations": {
            "inflow": inflow,
            "outflow": outflow,
            "excess": excess,
            "private_reserve_target": pr_target,
            "ret_client1_total": ret_client1,
            "ret_client2_total": ret_client2,
            "non_ret_total": non_ret,
            "trust_total": trust_val,
            "grand_total": grand_total,
            "liabilities_total": liabilities
        },
        "date": date_str
    }
    
    db.save_report(client_id, date_str, report_data)
    
    sacs_filename = f"SACS_{client['name'].replace(' ', '_')}_{date_str}.pdf"
    tcc_filename = f"TCC_{client['name'].replace(' ', '_')}_{date_str}.pdf"
    
    sacs_path = os.path.join(REPORTS_DIR, sacs_filename)
    tcc_path = os.path.join(REPORTS_DIR, tcc_filename)
    
    pdf_generator.generate_sacs(sacs_path, report_data)
    pdf_generator.generate_tcc(tcc_path, report_data)
    
    return jsonify({
        "sacs_url": f"/reports/{sacs_filename}",
        "tcc_url": f"/reports/{tcc_filename}",
        "calculations": report_data["calculations"]
    })

@app.route('/reports/<filename>')
def serve_report(filename):
    return send_from_directory(REPORTS_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
