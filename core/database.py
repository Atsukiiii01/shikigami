import sqlite3
import json
from datetime import datetime

class ShikigamiCore:
    def __init__(self, db_name="shikigami_state.db"):
        """Initializes the engine and connects to the foundational memory."""
        # THE FIX: Allow APScheduler worker threads to interact with the main thread's DB
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._build_foundation()

    def _build_foundation(self):
        """Creates the absolute bare-metal tables required for a state-aware engine."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                ip_address TEXT PRIMARY KEY,
                first_seen TEXT,
                last_seen TEXT,
                open_ports TEXT,  
                service_hash TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                ip_address TEXT,
                alert_type TEXT,
                description TEXT
            )
        ''')
        self.conn.commit()
        print("[*] Foundation built: Database initialized and schema loaded.")

    def update_asset_state(self, ip_address, current_ports, current_hash):
        """The diffing logic. Compares current scan data against the database."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_ports_json = json.dumps(current_ports)
        newly_opened_ports = [] # Default to empty

        self.cursor.execute("SELECT open_ports, service_hash FROM assets WHERE ip_address = ?", (ip_address,))
        row = self.cursor.fetchone()

        if row is None:
            print(f"[+] [NEW HOST] Discovered {ip_address}")
            self.cursor.execute('''
                INSERT INTO assets (ip_address, first_seen, last_seen, open_ports, service_hash)
                VALUES (?, ?, ?, ?, ?)
            ''', (ip_address, now, now, current_ports_json, current_hash))
            self._log_alert(ip_address, "NEW_HOST", f"Discovered with ports {current_ports}")
            newly_opened_ports = current_ports # All ports are new on a new host
        else:
            old_ports_json, old_hash = row
            old_ports = json.loads(old_ports_json)

            added_ports = list(set(current_ports) - set(old_ports))
            
            if added_ports:
                print(f"[!] [STATE CHANGE] {ip_address} opened new ports: {added_ports}")
                self._log_alert(ip_address, "PORT_OPENED", f"New ports detected: {added_ports}")
                newly_opened_ports = added_ports # Pass the delta out
            
            if old_hash != current_hash:
                print(f"[!] [MUTATION] {ip_address} service hash changed!")
                self._log_alert(ip_address, "SERVICE_MUTATION", "Banner/Service hash altered.")

            self.cursor.execute('''
                UPDATE assets 
                SET last_seen = ?, open_ports = ?, service_hash = ?
                WHERE ip_address = ?
            ''', (now, current_ports_json, current_hash, ip_address))
            
        self.conn.commit()
        return newly_opened_ports # Send the actionable intelligence back

    def _log_alert(self, ip_address, alert_type, description):
        """Saves actionable intelligence to the database."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''
            INSERT INTO alerts (timestamp, ip_address, alert_type, description)
            VALUES (?, ?, ?, ?)
        ''', (now, ip_address, alert_type, description))
        self.conn.commit()