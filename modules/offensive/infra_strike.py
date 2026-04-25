import ftplib
import paramiko
import time

def strike_ftp(ip_address, port=21):
    """Surgical Strike: Checks for Anonymous FTP access."""
    print(f"\n[*] [ENGAGING CLAWS] Testing {ip_address}:{port} for Anonymous FTP...")
    try:
        ftp = ftplib.FTP()
        ftp.connect(ip_address, port, timeout=5)
        ftp.login('anonymous', 'anonymous@example.com')
        print(f"[!!!] CRITICAL HIT: Anonymous FTP access allowed on {ip_address}:{port}")
        ftp.quit()
        return True
    except ftplib.all_errors:
        print(f"[-] Strike failed. FTP on {ip_address}:{port} is secured.")
        return False

def strike_ssh(ip_address, port=22):
    """Surgical Strike: Tests a micro-list of common default credentials."""
    print(f"\n[*] [ENGAGING CLAWS] Sniping default SSH credentials on {ip_address}:{port}...")
    default_creds = [
        ('root', 'root'),
        ('root', 'toor'),
        ('admin', 'admin'),
        ('pi', 'raspberry')
    ]
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    for username, password in default_creds:
        try:
            client.connect(ip_address, port=port, username=username, password=password, timeout=3)
            print(f"[!!!] CRITICAL HIT: SSH Default Credentials found on {ip_address}:{port} -> {username}:{password}")
            client.close()
            return True
        except paramiko.AuthenticationException:
            pass # Wrong credentials
        except Exception:
            break # Connection dropped
            
    print(f"[-] Strike failed. No default SSH credentials worked on {ip_address}:{port}.")
    return False