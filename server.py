from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import datetime
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

verification_codes = {}

users_db = [
    {
        "username": "erosorgu",
        "email": "erosorgu@gmail.com",
        "password": "Memo.1334",
        "role": "Founder",
        "date": "01.06.2026",
        "queries_count": 4867
    }
]

system_stats = {
    "total_queries": 4867,
    "successful_queries": 4812,
    "database_records": "105M+"
}

LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EROPANEL | Giriş & Kayıt</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        bgBase: '#0a0f1c',
                        panelDark: '#111827',
                        cardDark: '#1f2937',
                        accentPrimary: '#2563eb',
                        accentHover: '#1d4ed8',
                        accentDanger: '#dc2626',
                        accentSuccess: '#059669',
                        borderSubtle: '#374151',
                        textMuted: '#9ca3af'
                    },
                    fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] }
                }
            }
        }
    </script>
    <style>
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #0a0f1c; color: #f3f4f6; }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <div id="toast-container" class="fixed top-5 right-5 z-50 flex flex-col gap-2"></div>
    <div class="w-full max-w-md p-4 relative z-10">
        <div class="text-center mb-6">
            <div class="inline-flex w-14 h-14 rounded-2xl bg-red-600/20 items-center justify-center border border-red-600/50 shadow-[0_0_20px_rgba(220,38,38,0.4)] mb-3">
                <i class="fa-solid fa-shield-halved text-red-600 text-2xl"></i>
            </div>
            <h1 class="text-red-600 font-black text-2xl tracking-widest leading-none">EROPANEL</h1>
            <p class="text-xs text-textMuted mt-1 uppercase tracking-widest font-semibold">VIP Çözüm Merkezi</p>
        </div>
        <div class="bg-cardDark border border-borderSubtle rounded-3xl p-6 sm:p-8 shadow-2xl">
            <div class="flex bg-bgBase p-1 rounded-xl mb-6 border border-borderSubtle">
                <button type="button" id="tab-login-btn" onclick="switchTab('login')" class="flex-1 py-2.5 rounded-lg text-xs font-bold bg-accentPrimary text-white shadow-md">Giriş Yap</button>
                <button type="button" id="tab-register-btn" onclick="switchTab('register')" class="flex-1 py-2.5 rounded-lg text-xs font-bold text-textMuted hover:text-white">Kayıt Ol</button>
            </div>
            <form id="form-login" onsubmit="handleLogin(event)" class="space-y-4">
                <div>
                    <label class="block text-xs font-medium text-textMuted mb-1.5">Kullanıcı Adı veya Gmail</label>
                    <input type="text" id="login-username" required placeholder="Kullanıcı adınız..." class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 text-sm outline-none focus:border-accentPrimary">
                </div>
                <div>
                    <label class="block text-xs font-medium text-textMuted mb-1.5">Şifre</label>
                    <input type="password" id="login-password" required placeholder="••••••••" class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 text-sm outline-none focus:border-accentPrimary">
                </div>
                <button type="submit" class="w-full bg-accentPrimary hover:bg-accentHover text-white py-3.5 rounded-xl font-bold text-sm shadow-lg shadow-blue-500/20 mt-2">Sisteme Giriş Yap</button>
            </form>
            <div id="form-register" class="hidden">
                <div id="step-register-fields" class="space-y-4">
                    <div>
                        <label class="block text-xs font-medium text-textMuted mb-1.5">Kullanıcı Adı</label>
                        <input type="text" id="reg-username" required placeholder="Kullanıcı adı..." class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 text-sm outline-none focus:border-accentPrimary">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-textMuted mb-1.5">E-Posta Adresi (@gmail.com)</label>
                        <input type="email" id="reg-email" required placeholder="ornek@gmail.com" class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 text-sm outline-none focus:border-accentPrimary">
                    </div>
                    <div>
                        <label class="block text-xs font-medium text-textMuted mb-1.5">Şifre</label>
                        <input type="password" id="reg-password" required placeholder="••••••••" class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 text-sm outline-none focus:border-accentPrimary">
                    </div>
                    <button type="button" id="btn-send-code" onclick="handleRegisterRequest()" class="w-full bg-accentSuccess hover:bg-emerald-700 text-white py-3.5 rounded-xl font-bold text-sm shadow-lg mt-2">Kod Gönder</button>
                </div>
                <div id="step-verify-fields" class="space-y-4 hidden">
                    <div class="text-center mb-4">
                        <h3 class="text-white font-bold text-sm">Onay Kodu Girin</h3>
                        <p class="text-xs text-textMuted mt-1" id="verify-email-text"></p>
                    </div>
                    <input type="text" id="reg-code" maxlength="6" required placeholder="6 Haneli Kod" class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 text-center tracking-widest font-bold text-lg outline-none focus:border-accentPrimary">
                    <button type="button" onclick="handleVerifyCode()" class="w-full bg-accentSuccess text-white py-3.5 rounded-xl font-bold text-sm">Onayla & Kayıt Ol</button>
                </div>
            </div>
        </div>
    </div>
    <script>
        const API_URL = "/api";
        function showToast(msg, type='success') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `bg-panelDark border border-accentSuccess text-white rounded-lg px-4 py-3 shadow-xl text-xs font-semibold`;
            toast.innerText = msg;
            container.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }
        function switchTab(tab) {
            if(tab === 'login') {
                document.getElementById('form-login').classList.remove('hidden');
                document.getElementById('form-register').classList.add('hidden');
                document.getElementById('tab-login-btn').className = "flex-1 py-2.5 rounded-lg text-xs font-bold bg-accentPrimary text-white shadow-md";
                document.getElementById('tab-register-btn').className = "flex-1 py-2.5 rounded-lg text-xs font-bold text-textMuted";
            } else {
                document.getElementById('form-register').classList.remove('hidden');
                document.getElementById('form-login').classList.add('hidden');
                document.getElementById('tab-register-btn').className = "flex-1 py-2.5 rounded-lg text-xs font-bold bg-accentSuccess text-white shadow-md";
                document.getElementById('tab-login-btn').className = "flex-1 py-2.5 rounded-lg text-xs font-bold text-textMuted";
            }
        }
        let pendingUser = null;
        async function handleRegisterRequest() {
            const username = document.getElementById('reg-username').value.trim();
            const email = document.getElementById('reg-email').value.trim();
            const password = document.getElementById('reg-password').value.trim();

            if(!username || !email || !password) {
                showToast('Lütfen tüm alanları doldurun!', 'error');
                return;
            }

            const btn = document.getElementById('btn-send-code');
            btn.innerHTML = 'Gönderiliyor...';
            btn.disabled = true;

            try {
                const res = await fetch(`${API_URL}/send-code`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, email})
                });
                const data = await res.json();
                if(res.ok) {
                    pendingUser = {username, email, password};
                    document.getElementById('step-register-fields').classList.add('hidden');
                    document.getElementById('step-verify-fields').classList.remove('hidden');
                    document.getElementById('verify-email-text').innerText = email;
                    showToast('Kod gönderildi!');
                } else { 
                    showToast(data.error || 'Hata oluştu', 'error'); 
                }
            } catch(err) {
                showToast('Bağlantı hatası!', 'error');
            } finally {
                btn.innerHTML = 'Kod Gönder';
                btn.disabled = false;
            }
        }
        async function handleVerifyCode() {
            const code = document.getElementById('reg-code').value.trim();
            if(!code) {
                showToast('Lütfen onay kodunu girin!', 'error');
                return;
            }
            try {
                const res = await fetch(`${API_URL}/verify-and-register`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({...pendingUser, code})
                });
                const data = await res.json();
                if(res.ok) {
                    showToast('Kayıt başarılı!');
                    switchTab('login');
                } else { 
                    showToast(data.error || 'Kod hatalı!', 'error'); 
                }
            } catch(err) {
                showToast('Bağlantı hatası!', 'error');
            }
        }
        async function handleLogin(e) {
            e.preventDefault();
            const username = document.getElementById('login-username').value.trim();
            const password = document.getElementById('login-password').value.trim();
            const res = await fetch(`${API_URL}/login`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username, password})});
            const data = await res.json();
            if(res.ok) {
                localStorage.setItem('eropanel_current_user', JSON.stringify(data.user));
                window.location.href = '/panel';
            } else { showToast(data.error, 'error'); }
        }
    </script>
</body>
</html>
"""

PANEL_PAGE_HTML = """
<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EROPANEL | VIP PRO</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        bgBase: '#0a0f1c',
                        panelDark: '#111827',
                        cardDark: '#1f2937',
                        accentPrimary: '#2563eb',
                        accentHover: '#1d4ed8',
                        accentDanger: '#dc2626',
                        accentSuccess: '#059669',
                        borderSubtle: '#374151',
                        textMuted: '#9ca3af'
                    },
                    fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] }
                }
            }
        }
    </script>
    <style>
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #0a0f1c; color: #f3f4f6; }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 10px; }
        .fade-in { animation: fadeIn 0.3s ease-in-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        .glass-effect { background: rgba(31, 41, 55, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .api-raw-box { background: #111827; color: #f3f4f6; padding: 20px; border-radius: 12px; border: 1px solid #374151; overflow-x: auto; white-space: pre-wrap; font-size: 14px; line-height: 1.6; }
    </style>
</head>
<body class="min-h-screen flex flex-col lg:flex-row overflow-x-hidden">

    <div id="toast-container" class="fixed top-5 right-5 z-50 flex flex-col gap-2"></div>

    <!-- MOBILE HEADER -->
    <header class="lg:hidden h-16 bg-panelDark border-b border-borderSubtle flex items-center justify-between px-4 shrink-0 relative z-40">
        <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-lg bg-red-600/20 flex items-center justify-center border border-red-600/50">
                <i class="fa-solid fa-shield-halved text-red-600 text-sm"></i>
            </div>
            <h1 class="text-red-600 font-black text-lg tracking-widest">EROPANEL</h1>
        </div>
        <button onclick="toggleMobileSidebar()" class="text-white text-xl p-2 focus:outline-none">
            <i class="fa-solid fa-bars" id="mobile-menu-icon"></i>
        </button>
    </header>

    <!-- SIDEBAR -->
    <aside id="sidebar" class="fixed lg:static inset-y-0 left-0 transform -translate-x-full lg:translate-x-0 transition-transform duration-300 w-72 bg-panelDark border-r border-borderSubtle flex flex-col h-full shadow-2xl z-50 shrink-0">
        <div class="h-20 hidden lg:flex items-center px-6 border-b border-borderSubtle shrink-0 bg-gradient-to-r from-panelDark to-bgBase">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-red-600/20 flex items-center justify-center border border-red-600/50 shadow-[0_0_15px_rgba(220,38,38,0.4)]">
                    <i class="fa-solid fa-shield-halved text-red-600 text-xl"></i>
                </div>
                <div>
                    <h1 class="text-red-600 font-black text-xl tracking-widest leading-none">EROPANEL</h1>
                    <span class="text-[10px] text-gray-400 font-semibold tracking-widest uppercase">VIP Çözüm Merkezi</span>
                </div>
            </div>
        </div>

        <div class="p-6 border-b border-borderSubtle flex items-center gap-4 shrink-0 mt-12 lg:mt-0">
            <img id="sidebar-avatar" src="https://ui-avatars.com/api/?name=User&background=2563eb&color=fff&size=128" alt="Profil" class="w-12 h-12 rounded-xl border-2 border-borderSubtle shrink-0">
            <div class="flex-1 overflow-hidden">
                <div class="text-white font-semibold text-sm truncate" id="sidebar-display-name">Yükleniyor...</div>
                <div class="text-xs text-textMuted truncate flex items-center gap-1 mt-0.5">
                    <i class="fa-solid fa-crown text-yellow-500 text-[10px]"></i> <span id="sidebar-role-badge">Bağlanıyor</span>
                </div>
            </div>
        </div>

        <nav class="p-4 space-y-1.5 flex-1 overflow-y-auto" id="sidebar-nav">
            <a href="#" onclick="openMenu(event, 'dashboard')" class="nav-btn active bg-accentPrimary/10 text-accentPrimary border border-accentPrimary/30 px-4 py-3 rounded-xl text-sm transition-all flex items-center gap-3 font-medium">
                <i class="fa-solid fa-chart-line w-5 text-center text-lg"></i> Genel Bakış
            </a>

            <div class="pt-5 pb-2 px-4 text-[10px] font-bold text-textMuted uppercase tracking-widest">Sorgu Panelleri</div>
            
            <button onclick="toggleAccordion('acc-mernis')" class="w-full flex items-center justify-between text-gray-400 hover:text-white hover:bg-white/5 px-4 py-2.5 rounded-xl text-sm transition-all">
                <div class="flex items-center gap-3"><i class="fa-solid fa-id-card w-5 text-center"></i> Kimlik Çözümleri</div>
                <i id="acc-mernis-icon" class="fa-solid fa-chevron-right text-[10px] opacity-50 transition-transform duration-300"></i>
            </button>
            <div id="acc-mernis" class="pl-11 space-y-1 mt-1 hidden">
                <a href="#" onclick="openMenu(event, 'panel-tc')" class="sub-nav-btn block text-gray-400 hover:text-white text-xs py-2 transition-colors">TC Detay Sorgu</a>
                <a href="#" onclick="openMenu(event, 'panel-adsoyad')" class="sub-nav-btn block text-gray-400 hover:text-white text-xs py-2 transition-colors">Ad Soyad (Kapsamlı)</a>
            </div>

            <button onclick="logout()" class="w-full text-left text-accentDanger hover:text-white hover:bg-accentDanger/10 px-4 py-3 rounded-xl text-sm transition-all flex items-center gap-3 mt-4">
                <i class="fa-solid fa-right-from-bracket w-5 text-center"></i> Çıkış Yap
            </button>
        </nav>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="flex-1 flex flex-col h-full bg-bgBase relative z-10 overflow-y-auto w-full">
        <div class="p-4 sm:p-8 relative">
            <div class="max-w-[1600px] mx-auto w-full">

                <!-- 1. DASHBOARD -->
                <div id="dashboard" class="page-content fade-in space-y-6">
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
                        <div class="glass-effect rounded-2xl p-6 relative overflow-hidden group">
                            <h3 class="text-textMuted text-sm font-medium mb-1">Toplam Sorgu</h3>
                            <div class="text-4xl font-black text-white" id="stat-user-queries">0</div>
                        </div>
                    </div>
                </div>

                <!-- 2. TC DETAY SORGU -->
                <div id="panel-tc" class="page-content hidden fade-in space-y-6">
                    <div class="bg-cardDark border border-borderSubtle rounded-2xl shadow-xl overflow-hidden p-6 sm:p-8">
                        <h3 class="text-white font-bold mb-4">TC Kimlik Detaylı Analiz</h3>
                        <div class="flex flex-col sm:flex-row gap-4">
                            <input type="text" id="api-tc-input" maxlength="11" placeholder="TC Kimlik No" class="w-full bg-bgBase border-2 border-borderSubtle text-white rounded-xl px-4 py-3.5 outline-none focus:border-accentPrimary">
                            <button onclick="runProxyQuery('tc', {tc: document.getElementById('api-tc-input').value}, 'tc-result', 'tc-raw')" class="bg-accentPrimary text-white px-8 py-3.5 rounded-xl font-bold">Sorgula</button>
                        </div>
                        <div id="tc-result" class="hidden mt-6 pt-6 border-t border-borderSubtle">
                            <div class="bg-panelDark border border-borderSubtle rounded-xl p-5">
                                <div id="tc-raw" class="api-raw-box">// Sonuç bekleniyor...</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AD SOYAD -->
                <div id="panel-adsoyad" class="page-content hidden fade-in space-y-6">
                    <div class="bg-cardDark border border-borderSubtle rounded-2xl shadow-xl overflow-hidden p-6 sm:p-8">
                        <h3 class="text-white font-bold mb-4">Ad Soyad Filtreleme</h3>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                            <input type="text" id="ad-input" placeholder="Ad" class="bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 text-sm outline-none focus:border-accentPrimary">
                            <input type="text" id="soyad-input" placeholder="Soyad" class="bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 text-sm outline-none focus:border-accentPrimary">
                        </div>
                        <button onclick="runProxyQuery('adsoyad', {ad: document.getElementById('ad-input').value, soyad: document.getElementById('soyad-input').value}, 'adsoyad-result', 'adsoyad-raw')" class="bg-accentPrimary text-white px-6 py-3 rounded-xl font-bold">Filtrele</button>
                        <div id="adsoyad-result" class="hidden mt-6"><div id="adsoyad-raw" class="api-raw-box"></div></div>
                    </div>
                </div>

            </div>
        </div>
    </main>

    <script>
        const API_URL = "/api";
        let currentUser = JSON.parse(localStorage.getItem('eropanel_current_user'));
        if (!currentUser) { window.location.href = '/'; }

        function toggleMobileSidebar() {
            document.getElementById('sidebar').classList.toggle('-translate-x-full');
        }

        function openMenu(event, pageId) {
            if(event) event.preventDefault();
            document.querySelectorAll('.page-content').forEach(el => el.classList.add('hidden'));
            document.getElementById(pageId).classList.remove('hidden');
            if(window.innerWidth < 1024) toggleMobileSidebar();
        }

        function toggleAccordion(id) {
            document.getElementById(id).classList.toggle('hidden');
        }

        window.addEventListener('DOMContentLoaded', async () => {
            if (currentUser) {
                document.getElementById('sidebar-display-name').innerText = currentUser.username;
                document.getElementById('sidebar-role-badge').innerText = currentUser.role;
            }
        });

        async function runProxyQuery(endpoint, params, resultId, rawOutputId) {
            const btn = event.currentTarget;
            btn.innerText = "İşleniyor...";
            btn.disabled = true;
            try {
                const res = await fetch(`${API_URL}/${endpoint}?${new URLSearchParams(params)}`);
                const data = await res.json();
                document.getElementById(rawOutputId).innerText = JSON.stringify(data.data || data, null, 2);
                document.getElementById(resultId).classList.remove('hidden');
            } catch(e) {
                document.getElementById(rawOutputId).innerText = "Hata oluştu.";
                document.getElementById(resultId).classList.remove('hidden');
            } finally {
                btn.innerText = "Sorgula";
                btn.disabled = false;
            }
        }

        function logout() {
            localStorage.removeItem('eropanel_current_user');
            window.location.href = '/';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(LOGIN_PAGE_HTML)

@app.route('/panel')
def panel():
    return render_template_string(PANEL_PAGE_HTML)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    u_in = data.get('username', '').strip().lower()
    pwd = data.get('password', '').strip()
    user = next((u for u in users_db if (u["username"].lower() == u_in or u["email"].lower() == u_in) and u["password"] == pwd), None)
    if not user:
        return jsonify({"success": False, "error": "Kullanıcı adı veya şifre hatalı!"}), 401
    return jsonify({"success": True, "user": user})

@app.route('/api/send-code', methods=['POST'])
def send_code():
    data = request.json
    email = data.get('email', '').strip().lower()
    username = data.get('username', '').strip()
    
    if not email or not email.endswith('@gmail.com'):
        return jsonify({"success": False, "error": "Geçersiz @gmail.com adresi!"}), 400

    if any(u["username"].lower() == username.lower() for u in users_db):
        return jsonify({"success": False, "error": "Bu kullanıcı adı zaten kullanımda!"}), 400
    if any(u["email"].lower() == email.lower() for u in users_db):
        return jsonify({"success": False, "error": "Bu e-posta adresi zaten kullanımda!"}), 400

    code = str(random.randint(100000, 999999))
    verification_codes[email] = code

    sender_email = "erosorgu@gmail.com"
    sender_password = "boia thcl owze vgir".replace(" ", "")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "EROPANEL - Hesap Dogrulama Kodu"
    msg["From"] = sender_email
    msg["To"] = email

    html = f"""
    <div style="background-color: #0a0f1c; color: #f3f4f6; padding: 30px; font-family: sans-serif; border-radius: 12px;">
        <h2 style="color: #dc2626;">EROPANEL Güvenlik Merkezi</h2>
        <p>Onay kodunuz:</p>
        <div style="background: #111827; padding: 15px; border-radius: 8px; text-align: center;">
            <span style="color: #2563eb; font-size: 28px; font-weight: bold; letter-spacing: 6px;">{code}</span>
        </div>
    </div>
    """
    msg.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        return jsonify({"success": True, "message": "Kod gönderildi."})
    except Exception as e:
        return jsonify({"success": False, "error": f"Mail Gönderilemedi: {str(e)}"}), 500

@app.route('/api/verify-and-register', methods=['POST'])
def verify_and_register():
    data = request.json
    username = data.get('username')
    email = data.get('email', '').strip().lower()
    password = data.get('password')
    code = data.get('code')

    if verification_codes.get(email) != code:
        return jsonify({"success": False, "error": "Kod hatalı!"}), 400

    new_user = {
        "username": username,
        "email": email,
        "password": password,
        "role": "Member",
        "date": datetime.datetime.now().strftime("%d.%m.%Y"),
        "queries_count": 0
    }
    users_db.append(new_user)
    if email in verification_codes:
        del verification_codes[email]
        
    return jsonify({"success": True, "message": "Kayıt başarılı!"})

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({"success": True, "users": users_db})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        "success": True,
        "total_users": len(users_db),
        "successful_queries": system_stats["successful_queries"],
        "database_records": system_stats["database_records"]
    })

@app.route('/api/tc', methods=['GET'])
def api_tc():
    tc = request.args.get('tc')
    try:
        resp = requests.get(f"http://arastir.vip/api/tc.php?tc={tc}", timeout=5)
        return jsonify({"success": True, "data": resp.json() if resp.headers.get('content-type', '').startswith('application/json') else {"raw": resp.text}})
    except Exception as e:
        return jsonify({"success": False, "error": "Sunucu hatası"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
