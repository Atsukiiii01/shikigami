import sqlite3
import json
from datetime import datetime

class ShikigamiCore:
    def __init__(self, db_name="data/shikigami_state.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._build_schema()

    def _build_schema(self):
        """
        Upgraded Schema: Tracks generic targets (IPs or Subdomains), 
        their parent root domains, and continuous state.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                target TEXT PRIMARY KEY,
                asset_type TEXT,
                root_domain TEXT,
                open_ports TEXT,
                state_hash TEXT,
                discovered_at TEXT,
                last_scanned TEXT
            )
        ''')
        self.conn.commit()

    def add_asset(self, target, asset_type="ip", root_domain=None):
        """
        Registers a newly discovered asset from the Recon module into the platform.
        Ignores duplicates.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute('''
            INSERT OR IGNORE INTO assets (target, asset_type, root_domain, open_ports, state_hash, discovered_at, last_scanned)
            VALUES (?, ?, ?, '[]', 'initial', ?, ?)
        ''', (target, asset_type, root_domain, now, now))
        self.conn.commit()

    def get_active_targets(self):
        """
        Fetches all known targets for the Orchestrator's continuous pulse loop.
        """
        self.cursor.execute('SELECT target FROM assets')
        return [row[0] for row in self.cursor.fetchall()]

    def update_asset_state(self, target, ports, state_hash):
        """
        Core Diffing Engine. Analyzes the delta and returns newly opened ports.
        """
        # Ensure the asset exists in the DB first (in case it was manually fed)
        self.add_asset(target, "unknown", "unknown")
        
        self.cursor.execute('SELECT open_ports, state_hash FROM assets WHERE target = ?', (target,))
        result = self.cursor.fetchone()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_ports_detected = []

        if result:
            old_ports_str, old_hash = result
            old_ports = json.loads(old_ports_str) if old_ports_str else []
            
            # Diff logic: Identify purely new attack surface
            new_ports_detected = [p for p in ports if p not in old_ports]
            
            if old_hash != 'initial' and state_hash != old_hash:
                print(f"[!] [MUTATION] {target} service hash changed!")

        ports_json = json.dumps(ports)
        self.cursor.execute('''
            UPDATE assets 
            SET open_ports = ?, state_hash = ?, last_scanned = ?
            WHERE target = ?
        ''', (ports_json, state_hash, now, target))
        
        self.conn.commit()
        return new_ports_detected