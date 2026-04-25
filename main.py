import os
from datetime import datetime
from apscheduler.schedulers.background import BlockingScheduler
from workers.tasks import execute_live_scan, execute_osint_recon
from core.database import ShikigamiCore

db_engine = ShikigamiCore("data/shikigami_state.db")

def trigger_distributed_scan():
    targets = db_engine.get_active_targets()
    if not targets:
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[*] [ORCHESTRATOR] {now} | Asset database empty. Waiting for Recon task...")
        return

    now = datetime.now().strftime("%H:%M:%S")
    print(f"[*] [ORCHESTRATOR] {now} | Dispatching {len(targets)} active assets to Celery queue...")
    for target in targets:
        execute_live_scan.delay(target)

def trigger_recon_loop():
    """Explicit wrapper to ensure Orchestrator logs the OSINT strike."""
    target_org = "vulnweb.com"
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[*] [ORCHESTRATOR] {now} | Dispatching THE SHOVEL for {target_org}...")
    execute_osint_recon.delay(target_org)

if __name__ == "__main__":
    print(r"""
     _____ _     _ _    _                       _ 
    /  ___| |   (_) |  (_)                     (_)
    \ `--.| |__  _| | ___  __ _  __ _ _ __ ___  _ 
     `--. \ '_ \| | |/ / |/ _` |/ _` | '_ ` _ \| |
    /\__/ / | | | |   <| | (_| | (_| | | | | | | |
    \____/|_| |_|_|_|\_\_|\__, |\__,_|_| |_| |_|_|
    """)
    print("[*] Booting Autonomous CART Orchestrator...")
    
    if not os.path.exists("data"):
        os.makedirs("data")
        
    db_engine.add_asset("127.0.0.1", asset_type="ip", root_domain="localhost")
        
    scheduler = BlockingScheduler()
    
    # THE FAST LOOP: Pulse known assets (Increased misfire tolerance to 60s)
    scheduler.add_job(
        trigger_distributed_scan, 
        'interval', 
        seconds=30, 
        next_run_time=datetime.now(),
        misfire_grace_time=60 
    )
    
    # THE SLOW LOOP: OSINT Recon (Increased misfire tolerance)
    scheduler.add_job(
        trigger_recon_loop, 
        'interval', 
        hours=24, 
        next_run_time=datetime.now(),
        misfire_grace_time=60
    )
    
    try:
        print(f"[*] Orchestrator is LIVE. Press Ctrl+C to stop.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[*] Shutting down Orchestrator...")