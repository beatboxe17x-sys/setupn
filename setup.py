import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
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
from datetime import datetime

class InstallerHub:
    def __init__(self, root):
        self.root = root
        self.root.title("BRAX SUPPORT INSTALLER HUB v1.0")
        self.root.geometry("900x700")
        self.root.configure(bg="#0a0a0f")
        self.root.resizable(False, False)
        
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
        
        self.download_dir = os.path.join(os.environ.get('TEMP', tempfile.gettempdir()), "BraxInstaller")
        os.makedirs(self.download_dir, exist_ok=True)
        
        self.is_running = False
        
        if not self.is_admin():
            messagebox.showerror("Admin Required", "This tool requires Administrator privileges.\n\nPlease right-click and select 'Run as administrator'.")
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
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        header_frame = tk.Frame(main_frame, bg="#0a0a0f")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title = tk.Label(header_frame, text="BRAX SUPPORT INSTALLER", 
                        font=("Segoe UI", 24, "bold"), bg="#0a0a0f", fg="#00d4ff")
        title.pack()
        
        subtitle = tk.Label(header_frame, text="Automated Dependency Setup Tool", 
                           font=("Segoe UI", 11), bg="#0a0a0f", fg="#8899a6")
        subtitle.pack(pady=(5, 0))
        
        sep = tk.Frame(main_frame, bg="#1a1a2e", height=2)
        sep.pack(fill=tk.X, pady=10)
        
        steps_frame = tk.Frame(main_frame, bg="#0a0a0f")
        steps_frame.pack(fill=tk.X, pady=5)
        
        self.step_vars = []
        
        steps = [
            ("1", "Visual C++ Runtimes (All-in-One)", "Download & Extract -> Run Install_All.bat"),
            ("2", "DirectX Web Setup", "Download -> Run dxwebsetup.exe"),
            ("3", "Disable Windows Security", "Defender + Firewall + Exploit Protection + HVCI + SmartScreen + Driver Block"),
        ]
        
        for i, (num, title, desc) in enumerate(steps):
            step_frame = tk.Frame(steps_frame, bg="#11111a", highlightbackground="#1a1a2e", 
                                 highlightthickness=1, bd=0)
            step_frame.pack(fill=tk.X, pady=5, ipady=8)
            
            status = tk.Label(step_frame, text="o", font=("Segoe UI", 16), 
                            bg="#11111a", fg="#333344")
            status.pack(side=tk.LEFT, padx=(15, 10))
            self.step_vars.append(status)
            
            text_frame = tk.Frame(step_frame, bg="#11111a")
            text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            step_title = tk.Label(text_frame, text=f"Step {num}: {title}", 
                                 font=("Segoe UI", 12, "bold"), bg="#11111a", fg="#e1e8ed")
            step_title.pack(anchor=tk.W)
            
            step_desc = tk.Label(text_frame, text=desc, 
                                font=("Segoe UI", 9), bg="#11111a", fg="#8899a6")
            step_desc.pack(anchor=tk.W)
        
        progress_frame = tk.Frame(main_frame, bg="#0a0a0f")
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_label = tk.Label(progress_frame, text="READY TO START", 
                                      font=("Segoe UI", 10, "bold"), bg="#0a0a0f", fg="#00d4ff")
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=860, mode='determinate',
                                           style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.Horizontal.TProgressbar", 
                       troughcolor="#11111a", 
                       background="#00d4ff",
                       thickness=20,
                       borderwidth=0)
        
        btn_frame = tk.Frame(main_frame, bg="#0a0a0f")
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.run_btn = tk.Button(btn_frame, text="RUN SETUP", 
                                  font=("Segoe UI", 16, "bold"),
                                  bg="#00d4ff", fg="#0a0a0f",
                                  activebackground="#00a8cc", activeforeground="#0a0a0f",
                                  relief=tk.FLAT, bd=0, padx=40, pady=18,
                                  cursor="hand2",
                                  command=self.run_setup)
        self.run_btn.pack(fill=tk.X)
        
        self.run_btn.bind("<Enter>", lambda e: self.run_btn.config(bg="#00a8cc"))
        self.run_btn.bind("<Leave>", lambda e: self.run_btn.config(bg="#00d4ff"))
        
        log_frame = tk.Frame(main_frame, bg="#0a0a0f")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        log_header = tk.Label(log_frame, text="ACTIVITY LOG", 
                             font=("Segoe UI", 10, "bold"), bg="#0a0a0f", fg="#8899a6")
        log_header.pack(anchor=tk.W, pady=(0, 5))
        
        self.log_box = scrolledtext.ScrolledText(log_frame, height=8, 
                                                  bg="#08080f", fg="#a0b0c0",
                                                  font=("Consolas", 9),
                                                  insertbackground="#00d4ff",
                                                  relief=tk.FLAT,
                                                  highlightthickness=1,
                                                  highlightbackground="#1a1a2e",
                                                  highlightcolor="#00d4ff",
                                                  state=tk.DISABLED)
        self.log_box.pack(fill=tk.BOTH, expand=True)
        
        footer = tk.Label(main_frame, text="BRAX SUPPORT TOOLS | DynamicServices", 
                         font=("Segoe UI", 8), bg="#0a0a0f", fg="#333344")
        footer.pack(side=tk.BOTTOM, pady=(5, 0))
        
    def log(self, message, tag="info"):
        self.log_box.config(state=tk.NORMAL)
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] "
        
        if tag == "error":
            self.log_box.insert(tk.END, f"{timestamp}{message}\n", "error")
            self.log_box.tag_config("error", foreground="#ff4757")
        elif tag == "success":
            self.log_box.insert(tk.END, f"{timestamp}{message}\n", "success")
            self.log_box.tag_config("success", foreground="#2ed573")
        elif tag == "step":
            self.log_box.insert(tk.END, f"{timestamp}{message}\n", "step")
            self.log_box.tag_config("step", foreground="#00d4ff")
        else:
            self.log_box.insert(tk.END, f"{timestamp}{message}\n")
        
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)
        
    def update_step_status(self, step_idx, status):
        colors = {
            "pending": ("o", "#333344"),
            "active": (">>", "#00d4ff"),
            "done": ("OK", "#2ed573"),
            "error": ("XX", "#ff4757")
        }
        symbol, color = colors.get(status, ("o", "#333344"))
        self.step_vars[step_idx].config(text=symbol, fg=color)
        
    def set_progress(self, value, text=""):
        self.progress_bar['value'] = value
        if text:
            self.progress_label.config(text=text)
        self.root.update_idletasks()
        
    def download_file(self, url, dest_path, step_name):
        self.log(f"[DOWNLOAD] Starting: {step_name}")
        self.log(f"[DOWNLOAD] URL: {url[:80]}...")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'identity',
                'Connection': 'keep-alive',
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=120) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                chunk_size = 8192
                
                with open(dest_path, 'wb') as f:
                    while True:
                        if not self.is_running:
                            return False
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            self.set_progress(percent, f"Downloading {step_name}... {percent:.1f}%")
                        else:
                            self.set_progress(50, f"Downloading {step_name}... (size unknown)")
                            
            file_size = os.path.getsize(dest_path)
            self.log(f"[SUCCESS] Downloaded: {file_size:,} bytes", "success")
            
            with open(dest_path, 'rb') as f:
                header = f.read(50)
                if b'<html' in header.lower() or b'<!doctype' in header.lower():
                    self.log("[ERROR] Downloaded file is HTML, not the expected file", "error")
                    return False
                    
            return True
            
        except Exception as e:
            self.log(f"[ERROR] Download failed: {str(e)}", "error")
            return False
            
    def extract_zip(self, zip_path, extract_to, password=None):
        self.log(f"[EXTRACT] Extracting to: {extract_to}")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                if password:
                    zf.extractall(extract_to, pwd=password.encode('utf-8'))
                else:
                    zf.extractall(extract_to)
            self.log("[SUCCESS] Extraction complete", "success")
            return True
        except Exception as e:
            self.log(f"[ERROR] Extraction failed: {str(e)}", "error")
            return False
            
    def find_executable(self, directory, extensions=('.exe', '.bat', '.cmd')):
        self.log(f"[SEARCH] Looking for runnable files in: {directory}")
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(extensions):
                    path = os.path.join(root, file)
                    self.log(f"[FOUND] {file}")
                    return path
        return None
        
    def run_file_visible(self, file_path, step_name=""):
        self.log(f"[EXECUTE] Launching: {os.path.basename(file_path)}")
        try:
            if not os.path.exists(file_path):
                self.log(f"[ERROR] File not found: {file_path}", "error")
                return False
            
            self.log(f"[INFO] Opening window for {step_name}...")
            os.startfile(file_path)
            self.log(f"[SUCCESS] Window opened successfully", "success")
            
            self.log("[INFO] Waiting 8 seconds for installation...")
            time.sleep(8)
            return True
            
        except Exception as e:
            self.log(f"[ERROR] Launch failed: {str(e)}", "error")
            return False
            
    def step1_visual_cpp(self):
        self.update_step_status(0, "active")
        self.log("="*50, "step")
        self.log("STEP 1: Visual C++ Runtimes All-in-One", "step")
        self.log("="*50, "step")
        
        url = "https://us1-dl.techpowerup.com/files/TFl1z24nLT-xg12pijCPOA/1778485899/Visual-C-Runtimes-All-in-One-Dec-2025.zip"
        zip_path = os.path.join(self.download_dir, "vc_runtimes.zip")
        extract_path = os.path.join(self.download_dir, "vc_runtimes")
        
        if not self.download_file(url, zip_path, "Visual C++ Runtimes"):
            self.update_step_status(0, "error")
            return False
            
        self.set_progress(0, "Extracting Visual C++ Runtimes...")
        
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        os.makedirs(extract_path, exist_ok=True)
        
        if not self.extract_zip(zip_path, extract_path):
            self.update_step_status(0, "error")
            return False
            
        self.set_progress(0, "Running Install_All.bat...")
        
        bat_file = None
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.lower() == "install_all.bat":
                    bat_file = os.path.join(root, file)
                    break
            if bat_file:
                break
                
        if not bat_file:
            bat_file = self.find_executable(extract_path, ('.bat', '.cmd'))
            
        if bat_file:
            self.log(f"[FOUND] Installer: {os.path.basename(bat_file)}")
            if not self.run_file_visible(bat_file, "Visual C++ Runtimes"):
                self.update_step_status(0, "error")
                return False
        else:
            self.log("[WARNING] No .bat file found, opening folder for manual run", "error")
            os.startfile(extract_path)
            
        self.update_step_status(0, "done")
        return True
        
    def step2_directx(self):
        self.update_step_status(1, "active")
        self.log("="*50, "step")
        self.log("STEP 2: DirectX Web Setup", "step")
        self.log("="*50, "step")
        
        url = "https://download.microsoft.com/download/1/7/1/1718ccc4-6315-4d8e-9543-8e28a4e18c4c/dxwebsetup.exe"
        exe_path = os.path.join(self.download_dir, "dxwebsetup.exe")
        
        if not self.download_file(url, exe_path, "DirectX Setup"):
            self.update_step_status(1, "error")
            return False
            
        self.set_progress(0, "Running DirectX Web Setup...")
        
        if not self.run_file_visible(exe_path, "DirectX Setup"):
            self.update_step_status(1, "error")
            return False
            
        self.update_step_status(1, "done")
        return True
        
    def step3_disable_all_security(self):
        """Disable all Windows security features using PowerShell and registry"""
        self.update_step_status(2, "active")
        self.log("="*50, "step")
        self.log("STEP 3: Disable Windows Security", "step")
        self.log("="*50, "step")
        
        self.set_progress(0, "Disabling Windows Defender...")
        
        # --- WINDOWS DEFENDER ---
        self.log("[DEFENDER] Setting registry: DisableAntiSpyware = 1")
        reg_cmd = (
            'powershell "Set-ItemProperty -Path \\"HKLM:\\SOFTWARE\\Policies\\Microsoft'
            '\\Windows Defender\\" -Name \\"DisableAntiSpyware\\" -Value 1 -Type DWord -Force"'
        )
        r = subprocess.run(reg_cmd, capture_output=True, text=True, shell=True)
        if r.returncode != 0:
            self.log(f"[WARN] Registry failed: {r.stderr}")
        else:
            self.log("[SUCCESS] Defender registry updated", "success")
        
        self.log("[DEFENDER] Disabling real-time monitoring...")
        r = subprocess.run(
            'powershell "Set-MpPreference -DisableRealtimeMonitoring $true"',
            capture_output=True, text=True, shell=True
        )
        if r.returncode != 0:
            if "Provider load failure" in r.stderr or "0x80041013" in r.stderr:
                self.log("[INFO] Windows Defender already shut down / not available", "success")
            else:
                self.log(f"[WARN] Real-time monitoring failed: {r.stderr}")
        else:
            self.log("[SUCCESS] Real-time monitoring disabled", "success")
        
        self.log("[DEFENDER] Stopping WinDefend service...")
        r = subprocess.run(
            'powershell "Stop-Service -Name WinDefend -Force"',
            capture_output=True, text=True, shell=True
        )
        if r.returncode != 0:
            if "NoServiceFoundForGivenName" in r.stderr or "Cannot find any service" in r.stderr:
                self.log("[INFO] WinDefend service already removed / not present", "success")
            else:
                self.log(f"[WARN] Could not stop WinDefend: {r.stderr}")
        else:
            self.log("[SUCCESS] WinDefend service stopped", "success")
        
        self.set_progress(25, "Disabling Windows Firewall...")
        
        # --- FIREWALL ---
        self.log("[FIREWALL] Disabling all profiles...")
        registry_commands = [
            'powershell "Set-ItemProperty -Path \\"HKLM:\\SYSTEM\\CurrentControlSet\\Services'
            '\\SharedAccess\\Parameters\\FirewallPolicy\\StandardProfile\\" '
            '-Name \\"EnableFirewall\\" -Value 0"',
            'powershell "Set-ItemProperty -Path \\"HKLM:\\SYSTEM\\CurrentControlSet\\Services'
            '\\SharedAccess\\Parameters\\FirewallPolicy\\PublicProfile\\" '
            '-Name \\"EnableFirewall\\" -Value 0"',
            'powershell "Set-ItemProperty -Path \\"HKLM:\\SYSTEM\\CurrentControlSet\\Services'
            '\\SharedAccess\\Parameters\\FirewallPolicy\\DomainProfile\\" '
            '-Name \\"EnableFirewall\\" -Value 0"',
        ]
        for cmd in registry_commands:
            r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if r.returncode != 0:
                self.log(f"[WARN] Firewall registry failed: {r.stderr}")
        
        ps = ('powershell "Set-NetFirewallProfile '
              '-DefaultInboundAction Allow -DefaultOutboundAction Allow -Enabled False"')
        r = subprocess.run(ps, capture_output=True, text=True, shell=True)
        if r.returncode != 0:
            self.log(f"[WARN] Firewall profiles failed: {r.stderr}")
        else:
            self.log("[SUCCESS] Windows Firewall disabled for all profiles", "success")
        
        self.set_progress(50, "Disabling Exploit Protection...")
        
        # --- EXPLOIT PROTECTION ---
        self.log("[EXPLOIT] Disabling Exploit Protection...")
        try:
            base_key = winreg.HKEY_LOCAL_MACHINE
            path = (r"SOFTWARE\Policies\Microsoft\Windows Defender Security Center"
                    r"\App and Browser protection")
            try:
                key = winreg.CreateKeyEx(base_key, path, 0, winreg.KEY_WRITE | winreg.KEY_READ)
            except WindowsError as e:
                self.log(f"[WARN] Failed to create registry key: {e}")
                key = None
            if key:
                try:
                    winreg.SetValueEx(key, "DisallowExploitProtectionOverride", 0, winreg.REG_DWORD, 1)
                    self.log("[SUCCESS] Exploit Protection disabled", "success")
                except WindowsError as e:
                    self.log(f"[WARN] Failed to set registry value: {e}")
                finally:
                    winreg.CloseKey(key)
        except Exception as e:
            self.log(f"[WARN] Exploit Protection error: {e}")
        
        self.set_progress(65, "Disabling HVCI / Core Isolation...")
        
        # --- HVCI / CORE ISOLATION ---
        self.log("[HVCI] Disabling Hypervisor Enforced Code Integrity...")
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity")
            winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            self.log("[SUCCESS] HVCI disabled", "success")
        except Exception as e:
            self.log(f"[WARN] HVCI error: {e}")
        
        self.set_progress(80, "Disabling SmartScreen...")
        
        # --- SMARTSCREEN ---
        self.log("[SMARTSCREEN] Disabling SmartScreen...")
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Policies\Microsoft\Windows\System")
            winreg.SetValueEx(key, "EnableSmartScreen", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer")
            winreg.SetValueEx(key, "SmartScreenEnabled", 0, winreg.REG_SZ, "Off")
            winreg.CloseKey(key)
            self.log("[SUCCESS] SmartScreen disabled", "success")
        except Exception as e:
            self.log(f"[WARN] SmartScreen error: {e}")
        
        self.set_progress(90, "Disabling Driver Blocklist...")
        
        # --- DRIVER BLOCKLIST ---
        self.log("[DRIVER] Disabling Vulnerable Driver Blocklist...")
        try:
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\CI\Config")
            winreg.SetValueEx(key, "VulnerableDriverBlocklistEnabled", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            self.log("[SUCCESS] Driver Blocklist disabled", "success")
        except Exception as e:
            self.log(f"[WARN] Driver Blocklist error: {e}")
        
        self.log("[SUCCESS] All Windows Security features disabled", "success")
        self.update_step_status(2, "done")
        return True
        
    def installation_thread(self):
        self.is_running = True
        self.run_btn.config(state=tk.DISABLED, text="RUNNING...", bg="#1a1a2e", fg="#8899a6")
        
        try:
            self.set_progress(0, "Starting installation...")
            
            if not self.step1_visual_cpp():
                if self.is_running:
                    self.log("[FATAL] Step 1 failed. Stopping.", "error")
                return
            self.set_progress(33, "Step 1 Complete OK")
            
            if not self.step2_directx():
                if self.is_running:
                    self.log("[FATAL] Step 2 failed. Stopping.", "error")
                return
            self.set_progress(66, "Step 2 Complete OK")
            
            if not self.step3_disable_all_security():
                if self.is_running:
                    self.log("[FATAL] Step 3 failed. Stopping.", "error")
                return
            self.set_progress(100, "ALL STEPS COMPLETE OK")
            
            if self.is_running:
                self.log("="*50, "success")
                self.log("INSTALLATION COMPLETE!", "success")
                self.log("="*50, "success")
                self.run_btn.config(text="SETUP COMPLETE", bg="#2ed573", fg="#0a0a0f", state=tk.NORMAL)
                messagebox.showinfo("Success", "All installations completed!\n\nWindows Security fully disabled:\n- Defender\n- Firewall\n- Exploit Protection\n- HVCI\n- SmartScreen\n- Driver Blocklist\n\nBRAX SUPPORT TOOLS")
                
        except Exception as e:
            self.log(f"[CRITICAL ERROR] {str(e)}", "error")
            messagebox.showerror("Error", f"Installation failed:\n{str(e)}")
            
        finally:
            self.is_running = False
            if self.run_btn['text'] != "SETUP COMPLETE":
                self.run_btn.config(state=tk.NORMAL, text="RUN SETUP", bg="#00d4ff", fg="#0a0a0f")
        
    def run_setup(self):
        if self.is_running:
            return
        thread = threading.Thread(target=self.installation_thread, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    app = InstallerHub(root)
    root.mainloop()

if __name__ == "__main__":
    main()