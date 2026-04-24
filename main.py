from core.database import ShikigamiCore
from workers.scheduler import start_scheduler
import os

if __name__ == "__main__":
    print(r"""
     _____ _     _ _    _                       _ 
    /  ___| |   (_) |  (_)                     (_)
    \ `--.| |__  _| | ___  __ _  __ _ _ __ ___  _ 
     `--. \ '_ \| | |/ / |/ _` |/ _` | '_ ` _ \| |
    /\__/ / | | | |   <| | (_| | (_| | | | | | | |
    \____/|_| |_|_|_|\_\_|\__, |\__,_|_| |_| |_|_|
                           __/ |                  
                          |___/                   
    """)
    print("[*] Initializing Continuous Attack Surface Management...")
    
    # Ensure data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")
        
    # 1. Boot the memory
    engine = ShikigamiCore("data/shikigami_state.db")
    
    # 2. Boot the muscle
    start_scheduler(engine)
    