import os
from datetime import datetime
from apscheduler.schedulers.background import BlockingScheduler
from workers.tasks import execute_live_scan

def trigger_distributed_scan(target_ip):
    """
    The Brain doesn't do the heavy lifting anymore. 
    It just pushes the target to the Redis queue.
    """
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[*] [ORCHESTRATOR] {now} | Dispatching target {target_ip} to Celery worker queue...")
    
    # The .delay() command fires the task into Redis asynchronously.
    execute_live_scan.delay(target_ip)

if __name__ == "__main__":
    print(r"""
     _____ _     _ _    _                       _ 
    /  ___| |   (_) |  (_)                     (_)
    \ `--.| |__  _| | ___  __ _  __ _ _ __ ___  _ 
     `--. \ '_ \| | |/ / |/ _` |/ _` | '_ ` _ \| |
    /\__/ / | | | |   <| | (_| | (_| | | | | | | |
    \____/|_| |_|_|_|\_\_|\__, |\__,_|_| |_| |_|_|
    """)
    print("[*] Booting Distributed CART Orchestrator...")
    
    if not os.path.exists("data"):
        os.makedirs("data")
        
    scheduler = BlockingScheduler()
    target = "127.0.0.1" 
    
    # Tell the brain to push a task to Redis every 30 seconds
    # (Setting next_run_time so it fires immediately on boot)
    scheduler.add_job(
        trigger_distributed_scan, 
        'interval', 
        seconds=30, 
        args=[target], 
        next_run_time=datetime.now()
    )
    
    try:
        print(f"[*] Orchestrator is LIVE. Press Ctrl+C to stop.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[*] Shutting down Orchestrator...")