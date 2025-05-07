from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify,Response
import joblib
import random
import serial
import time
import sqlite3
from datetime import datetime
from email_alert import send_alert_email
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Load trained model
try:
    model = joblib.load('models/blockage_rf_model.pkl')
except Exception as e:
    print(f"⚠️ Model load failed: {e}")
    model = None

# Arduino config
COM_PORT = 'COM5'
BAUD_RATE = 9600
ARDUINO_CONNECTED = False
arduino = None


def is_com_port_locked(port='COM5'):
    """Check if COM port is already in use"""
    try:
        with serial.Serial(port, BAUD_RATE, timeout=1) as test:
            return False
    except serial.SerialException:
        return True


def close_arduino():
    """Ensure Arduino port is closed on exit"""
    global arduino
    if arduino and arduino.is_open:
        arduino.close()
        print("🔌 Arduino port closed on exit")


# Register cleanup
import atexit

atexit.register(close_arduino)

# Try to connect to Arduino
if not is_com_port_locked(COM_PORT):
    try:
        arduino = serial.Serial(COM_PORT, BAUD_RATE, timeout=5.1)
        time.sleep(2)
        ARDUINO_CONNECTED = True
        print(f"✅ Connected to Arduino on {COM_PORT}")
    except Exception as e:
        print(f"❌ Arduino not connected: {e}")
        arduino = None
        ARDUINO_CONNECTED = False
else:
    print(f"⚠️ COM port {COM_PORT} is already in use")

def get_live_sensor_data():
    """Read sensor data from Arduino or simulate if disconnected"""
    sensor_data = {
        "location": f"Zone {random.randint(1, 10)}",
        "water_level": random.randint(0, 580),
        "flow_rate": round(random.uniform(0.1, 5.0), 2),
        "vibration": round(random.uniform(0.1, 10.0), 2),
        "gas_concentration": random.randint(100, 1000),
        "proximity": random.choice([0, 1]),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "triggered_sensor": "---"
    }

    global arduino, ARDUINO_CONNECTED

    if ARDUINO_CONNECTED:
        try:
            if arduino and arduino.is_open:
                line = arduino.readline().decode('utf-8').strip()
                if line:
                    print(f"Serial Data: {line}")
                    parts = line.split(',')

                    if len(parts) == 5:  # Now expecting 5 values
                        try:
                            sensor_data.update({
                                "water_level": int(parts[0]),
                                "flow_rate": float(parts[1]),
                                "vibration": float(parts[2]),
                                "gas_concentration": float(parts[3]),
                                "proximity": int(parts[4]),
                            })
                        except Exception as e:
                            print(f"⚠️ Invalid data from Arduino: {e}")
        except serial.SerialException as e:
            print(f"❌ Serial read error: {e}")
            ARDUINO_CONNECTED = False
            try:
                arduino.close()
                arduino = serial.Serial(COM_PORT, BAUD_RATE, timeout=5.1)
                ARDUINO_CONNECTED = True
                print(f"✅ Reconnected to Arduino")
            except:
                print("⚠️ Failed to reconnect to Arduino")

    return sensor_data
"""def get_live_sensor_data():
    //Read sensor data from Arduino or simulated values
    sensor_data = {
        "location": f"Zone {random.randint(1, 10)}",
        "water_level": random.randint(0, 580),
        "flow_rate": round(random.uniform(0.1, 5.0), 2),

        "vibration": round(random.uniform(0.1, 10.0), 2),
        "gas_concentration": random.randint(100, 1000),
        "proximity": random.choice([0, 1]),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "triggered_sensor": "---"
    }

    global arduino, ARDUINO_CONNECTED

    if ARDUINO_CONNECTED:
        try:
            if arduino and arduino.is_open:
                line = arduino.readline().decode('utf-8').strip()
                if line:
                    print(f"Serial Data: {line}")
                    parts = line.split(',')

                    if len(parts) == 5:
                        sensor_data.update({
                            "water_level": int(parts[0]),
                            "flow_rate": float(parts[1]),

                            "vibration": float(parts[2]),
                            "gas_concentration": float(parts[3]),
                            "proximity": int(parts[4]),
                        })
        except serial.SerialException as e:
            print(f"❌ Serial read error: {e}")
            ARDUINO_CONNECTED = False
            try:
                arduino.close()
                arduino = serial.Serial(COM_PORT, BAUD_RATE, timeout=5.1)
                ARDUINO_CONNECTED = True
                print(f"✅ Reconnected to Arduino")
            except Exception as re:
                print(f"⚠️ Failed to reconnect: {re}")

    return sensor_data
"""

"""def detect_blockage(sensor_data):
    //Simple blockage detection logic
    water_level = sensor_data['water_level']
    gas = sensor_data['gas_concentration']
    vibration = sensor_data['vibration']

    if water_level > 500:
        return "Flooding Detected", "Water Level"
    elif gas > 800:
        return "Gas Leak Detected", "Gas Concentration"
    elif vibration > 7.0:
        return "Pipe Crack Detected", "Vibration"
    else:
        return "Blockage Clear", "---"
"""
def detect_blockage(sensor_data):
    water_level = sensor_data['water_level']
    gas = sensor_data['gas_concentration']
    vibration = sensor_data['vibration']

    if water_level > 500:
        return "Flooding Detected", "Water Level"
    elif gas > 800:
        return "Gas Leak Detected", "Gas Concentration"
    elif vibration > 7.0:
        return "Pipe Crack Detected", "Vibration"
    else:
        return "Blockage Clear", "---"

@app.route('/')
def splash():
    return render_template('splash.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        flash("Registered successfully! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


"""@app.route('/live_data')
def live_data():
    sensor_data = get_live_sensor_data()
    status, triggered_sensor = detect_blockage(sensor_data)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to history
    try:
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute(""INSERT INTO blockage_history 
                        (location, timestamp, status, sensor) 
                        VALUES (?, ?, ?, ?)"",
                      (sensor_data['location'], timestamp, status, triggered_sensor))
            conn.commit()
    except Exception as e:
        print(f"❌ DB Write Error: {e}")

    return jsonify({
        "sensor_data": sensor_data,
        "status": status,
        "timestamp": timestamp
    })"""


@app.route('/live_data')
def live_data():
    sensor_data = get_live_sensor_data()
    status, triggered_sensor = detect_blockage(sensor_data)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to database
    try:
        with sqlite3.connect('database.db', timeout=5) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO blockage_history (location, timestamp, status, sensor) VALUES (?, ?, ?, ?)",
                      (sensor_data['location'], timestamp, status, triggered_sensor))
            conn.commit()
    except Exception as e:
        print(f"❌ DB Write Error: {e}")

    return jsonify({
        "sensor_data": sensor_data,
        "status": status,
        "timestamp": timestamp
    })
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        frequency = request.form['frequency']
        water_level = request.form['water_level']
        flow_rate = request.form['flow_rate']
        pressure = request.form['pressure']
        vibration = request.form['vibration']
        gas_concentration = request.form['gas_concentration']
        proximity = request.form['proximity']
        alerts = request.form['alerts']

        # Update DB
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("DELETE FROM config")  # Only keep one config row
        c.execute("""INSERT INTO config (email, frequency, water_level, flow_rate, pressure,
                     vibration, gas_concentration, proximity, alerts)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (email, frequency, water_level, flow_rate, pressure,
                   vibration, gas_concentration, proximity, alerts))
        conn.commit()
        conn.close()

    # Load existing settings
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM config LIMIT 1")
    row = c.fetchone()
    conn.close()

    if row:
        keys = ['email', 'frequency', 'water_level', 'flow_rate', 'pressure',
                'vibration', 'gas_concentration', 'proximity', 'alerts']
        settings = dict(zip(keys, row))
    else:
        settings = {k: '' for k in ['email', 'frequency', 'water_level', 'flow_rate', 'pressure',
                                    'vibration', 'gas_concentration', 'proximity', 'alerts']}

    return render_template('settings.html', settings=settings)

"""@app.route('/live_data')
def live_data():
    sensor_data = get_live_sensor_data()

    features = np.array([
        sensor_data['water_level'],
        sensor_data['flow_rate'],
        sensor_data['pressure'],
        sensor_data['vibration'],
        sensor_data['gas_concentration'],
        sensor_data['proximity'],
        0.0
    ]).reshape(1, -1)

    prediction = model.predict(features)[0]
    location = sensor_data['location']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    triggered_sensor = sensor_data.get('triggered_sensor', 'Unknown')

    if prediction == 1:
        status = 'Blockage Detected'
        send_alert_email(location, timestamp,triggered_sensor)  # send alert if blocked
    else:
        status = 'Clear'

    insert_history(location, timestamp, status, triggered_sensor)  # store in history

    return {
        "sensor_data": sensor_data,
        "status": status,
        "timestamp": timestamp
    }

"""
# Home Page
@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return render_template('home.html', username=None)
def insert_history(location, timestamp, status, sensor_triggered):
    try:
        with sqlite3.connect('database.db', timeout=5) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO blockage_history (location, timestamp, status, sensor) VALUES (?, ?, ?, ?)",
                      (location, timestamp, status, sensor_triggered))
            conn.commit()
    except sqlite3.OperationalError as e:
        print(f"❌ DB Error: {e}")
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, location, timestamp, status, sensor FROM blockage_history ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()

    return render_template('history.html', rows=rows)

@app.route('/download_history')
def download_history():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM blockage_history")
    rows = c.fetchall()
    conn.close()

    def generate():
        data = ['ID,Location,Timestamp,Status,Sensor\n']
        for row in rows:
            data.append(','.join(str(x) for x in row) + '\n')
        return data

    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=blockage_history.csv"})

@app.route('/help-center')
def help_center():
    return render_template('help_center.html')

@app.route('/report_issue', methods=['POST'])
def report_issue():
    issue = request.form['issue']
    # Save to DB or notify
    flash('Issue submitted successfully!', 'success')
    return redirect('/help-center')

@app.route('/submit_query', methods=['POST'])
def submit_query():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    # Store or email to support team
    flash('Query submitted successfully!', 'success')
    return redirect('/help-center')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


@app.route('/analytics-data')
def analytics_data():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Sensor Frequency
    c.execute("SELECT sensor, COUNT(*) FROM blockage_history WHERE sensor != '---' GROUP BY sensor")
    sensor_data = c.fetchall()

    # Blockages by Zone
    c.execute("SELECT location, COUNT(*) FROM blockage_history WHERE status = 'Blockage Detected' GROUP BY location")
    zone_data = c.fetchall()

    # Hourly Blockage Pattern
    c.execute("SELECT strftime('%H', timestamp), COUNT(*) FROM blockage_history GROUP BY strftime('%H', timestamp)")
    hour_data = c.fetchall()



    conn.close()

    return jsonify({
        "sensor": {row[0]: row[1] for row in sensor_data},
        "zone": {row[0]: row[1] for row in zone_data},
        "hourly": {row[0]: row[1] for row in hour_data}

    })


"""@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id, location, timestamp, status, sensor FROM blockage_history ORDER BY timestamp DESC")
        rows = c.fetchall()
        return render_template('history.html', rows=rows)
    finally:
        conn.close()"""


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))


# Create database tables if not exist
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS blockage_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  location TEXT,
                  timestamp TEXT,
                  status TEXT,
                  sensor TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS config
                 (email TEXT, frequency TEXT, water_level TEXT, flow_rate TEXT,
                  pressure TEXT, vibration TEXT, gas_concentration TEXT,
                  proximity TEXT, alerts TEXT)''')
    conn.commit()
    conn.close()


# Initialize database tables
init_db()

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
