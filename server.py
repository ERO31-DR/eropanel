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
CORS(app)

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
<body class="h-screen flex items-center justify-center overflow-hidden">
    <div id="toast-container" class="fixed top-5 right-5 z-50 flex flex-col gap-2"></div>
    <div class="w-full max-w-md p-6 relative z-10">
        <div class="text-center mb-8">
            <div class="inline-flex w-14 h-14 rounded-2xl bg-red-600/20 items-center justify-center border border-red-600/50 shadow-[0_0_20px_rgba(220,38,38,0.4)] mb-3">
                <i class="fa-solid fa-shield-halved text-red-600 text-2xl"></i>
            </div>
            <h1 class="text-red-600 font-black text-2xl tracking-widest leading-none">EROPANEL</h1>
            <p class="text-xs text-textMuted mt-1 uppercase tracking-widest font-semibold">VIP Çözüm Merkezi</p>
        </div>
        <div class="bg-cardDark border border-borderSubtle rounded-3xl p-8 shadow-2xl">
            <div class="flex bg-bgBase p-1 rounded-xl mb-6 border border-borderSubtle">
                <button id="tab-login-btn" onclick="switchTab('login')" class="flex-1 py-2.5 rounded-lg text-xs font-bold bg-accentPrimary text-white shadow-md">Giriş Yap</button>
                <button id="tab-register-btn" onclick="switchTab('register')" class="flex-1 py-2.5 rounded-lg text-xs font-bold text-textMuted hover:text-white">Kayıt Ol</button>
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
                <form id="step-register-fields" onsubmit="handleRegisterRequest(event)" class="space-y-4">
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
                    <button type="submit" class="w-full bg-accentSuccess hover:bg-emerald-700 text-white py-3.5 rounded-xl font-bold text-sm shadow-lg mt-2">Kod Gönder</button>
                </form>
                <form id="step-verify-fields" onsubmit="handleVerifyCode(event)" class="space-y-4 hidden">
                    <div class="text-center mb-4">
                        <h3 class="text-white font-bold text-sm">Onay Kodu Girin</h3>
                        <p class="text-xs text-textMuted mt-1" id="verify-email-text"></p>
                    </div>
                    <input type="text" id="reg-code" maxlength="6" required placeholder="6 Haneli Kod" class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 text-center tracking-widest font-bold text-lg outline-none focus:border-accentPrimary">
                    <button type="submit" class="w-full bg-accentSuccess text-white py-3.5 rounded-xl font-bold text-sm">Onayla & Kayıt Ol</button>
                </form>
            </div>
        </div>
    </div>
    <script>
        const API_URL = "https://eropanel.onrender.com/api";
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
        async function handleRegisterRequest(e) {
            e.preventDefault();
            const username = document.getElementById('reg-username').value.trim();
            const email = document.getElementById('reg-email').value.trim();
            const password = document.getElementById('reg-password').value.trim();
            const res = await fetch(`${API_URL}/send-code`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username, email})});
            const data = await res.json();
            if(res.ok) {
                pendingUser = {username, email, password};
                document.getElementById('step-register-fields').classList.add('hidden');
                document.getElementById('step-verify-fields').classList.remove('hidden');
                document.getElementById('verify-email-text').innerText = email;
                showToast('Kod gönderildi!');
            } else { showToast(data.error, 'error'); }
        }
        async function handleVerifyCode(e) {
            e.preventDefault();
            const code = document.getElementById('reg-code').value.trim();
            const res = await fetch(`${API_URL}/verify-and-register`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({...pendingUser, code})});
            if(res.ok) {
                showToast('Kayıt başarılı!');
                switchTab('login');
            } else { showToast('Kod hatalı!', 'error'); }
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
                    fontFamily: {
                        sans: ['Inter', 'system-ui', 'sans-serif'],
                    }
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
        ::-webkit-scrollbar-thumb:hover { background: #6b7280; }
        
        .fade-in { animation: fadeIn 0.3s ease-in-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        
        input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus, input:-webkit-autofill:active{
            -webkit-box-shadow: 0 0 0 30px #1f2937 inset !important;
            -webkit-text-fill-color: white !important;
        }

        .glass-effect {
            background: rgba(31, 41, 55, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .api-raw-box {
            font-family: 'Inter', sans-serif;
            background: #111827;
            color: #f3f4f6;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #374151;
            overflow-x: auto;
            white-space: pre-wrap;
            font-size: 14px;
            line-height: 1.6;
        }
    </style>
</head>
<body class="h-screen flex overflow-hidden selection:bg-accentPrimary selection:text-white">

    <div id="toast-container" class="fixed top-5 right-5 z-50 flex flex-col gap-2"></div>

    <!-- SIDEBAR -->
    <aside class="w-72 bg-panelDark border-r border-borderSubtle flex flex-col h-full shadow-2xl relative z-40">
        <!-- Logo -->
        <div class="h-20 flex items-center px-6 border-b border-borderSubtle shrink-0 bg-gradient-to-r from-panelDark to-bgBase">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-red-600/20 flex items-center justify-center border border-red-600/50 shadow-[0_0_15px_rgba(220,38,38,0.4)]">
                    <i class="fa-solid fa-shield-halved text-red-600 text-xl"></i>
                </div>
                <div>
                    <h1 class="text-red-600 font-black text-xl tracking-widest leading-none drop-shadow-[0_0_8px_rgba(220,38,38,0.8)]">EROPANEL</h1>
                    <span class="text-[10px] text-gray-400 font-semibold tracking-widest uppercase">VIP Çözüm Merkezi</span>
                </div>
            </div>
        </div>

        <div class="p-6 border-b border-borderSubtle flex items-center gap-4 shrink-0">
            <div class="relative">
                <img id="sidebar-avatar" src="https://ui-avatars.com/api/?name=User&background=2563eb&color=fff&size=128" alt="Profil" class="w-12 h-12 rounded-xl border-2 border-borderSubtle">
                <div class="absolute -bottom-1 -right-1 w-4 h-4 bg-accentSuccess border-2 border-panelDark rounded-full"></div>
            </div>
            <div class="flex-1 overflow-hidden">
                <div class="text-white font-semibold text-sm truncate" id="sidebar-display-name">Yükleniyor...</div>
                <div class="text-xs text-textMuted truncate flex items-center gap-1 mt-0.5">
                    <i class="fa-solid fa-crown text-yellow-500 text-[10px]"></i> <span id="sidebar-role-badge">Bağlanıyor</span>
                </div>
            </div>
        </div>

        <!-- Navigation -->
        <nav class="p-4 space-y-1.5 flex-1 overflow-y-auto" id="sidebar-nav">
            
            <a href="#" onclick="openMenu(event, 'dashboard')" class="nav-btn active bg-accentPrimary/10 text-accentPrimary border border-accentPrimary/30 px-4 py-3 rounded-xl text-sm transition-all flex items-center gap-3 font-medium">
                <i class="fa-solid fa-chart-line w-5 text-center text-lg"></i> Genel Bakış
            </a>

            <div class="pt-5 pb-2 px-4 text-[10px] font-bold text-textMuted uppercase tracking-widest">Sorgu Panelleri</div>
            
            <!-- Mernis & Kimlik -->
            <button onclick="toggleAccordion('acc-mernis')" class="w-full flex items-center justify-between text-gray-400 hover:text-white hover:bg-white/5 px-4 py-2.5 rounded-xl text-sm transition-all">
                <div class="flex items-center gap-3"><i class="fa-solid fa-id-card w-5 text-center"></i> Kimlik Çözümleri</div>
                <i id="acc-mernis-icon" class="fa-solid fa-chevron-right text-[10px] opacity-50 transition-transform duration-300"></i>
            </button>
            <div id="acc-mernis" class="pl-11 space-y-1 mt-1 hidden">
                <a href="#" onclick="openMenu(event, 'panel-tc')" class="sub-nav-btn block text-gray-400 hover:text-white text-xs py-2 transition-colors">TC Detay Sorgu</a>
                <a href="#" onclick="openMenu(event, 'panel-adsoyad')" class="sub-nav-btn block text-gray-400 hover:text-white text-xs py-2 transition-colors">Ad Soyad (Kapsamlı)</a>
            </div>

            <!-- Aile & Sülale -->
            <button onclick="toggleAccordion('acc-aile')" class="w-full flex items-center justify-between text-gray-400 hover:text-white hover:bg-white/5 px-4 py-2.5 rounded-xl text-sm transition-all">
                <div class="flex items-center gap-3"><i class="fa-solid fa-sitemap w-5 text-center"></i> Aile & Sülale</div>
                <i id="acc-aile-icon" class="fa-solid fa-chevron-right text-[10px] opacity-50 transition-transform duration-300"></i>
            </button>
            <div id="acc-aile" class="pl-11 space-y-1 mt-1 hidden">
                <a href="#" onclick="openMenu(event, 'panel-aile')" class="sub-nav-btn block text-gray-400 hover:text-white text-xs py-2 transition-colors">Aile Sorgu</a>
                <a href="#" onclick="openMenu(event, 'panel-sulale')" class="sub-nav-btn block text-gray-400 hover:text-white text-xs py-2 transition-colors">Sülale Sorgu</a>
                <a href="#" onclick="openMenu(event, 'panel-cocuk')" class="sub-nav-btn block text-gray-400 hover:text-white text-xs py-2 transition-colors">Çocuk Sorgu</a>
            </div>

            <!-- İletişim & GSM -->
            <button onclick="toggleAccordion('acc-gsm')" class="w-full flex items-center justify-between text-gray-400 hover:text-white hover:bg-white/5 px-4 py-2.5 rounded-xl text-sm transition-all">
                <div class="flex items-center gap-3"><i class="fa-solid fa-tower-cell w-5 text-center"></i> İletişim & GSM</div>
                <i id="acc-gsm-icon" class="fa-solid fa-chevron-right text-[10px] opacity-50 transition-transform duration-300"></i>
            </button>
            <div id="acc-gsm" class="pl-11 space-y-1 mt-1 hidden">
                <a href="#" onclick="openMenu(event, 'panel-gsmtc')" class="sub-nav-btn block text-gray-400 hover:text-white text-xs py-2 transition-colors">GSM'den TC Bulma</a>
                <a href="#" onclick="openMenu(event, 'panel-tcgsm')" class="sub-nav-btn block text-gray-400 hover:text-white text-xs py-2 transition-colors">TC'den GSM Bulma</a>
            </div>

            <!-- Kurum & Diğer -->
            <button onclick="toggleAccordion('acc-kurum')" class="w-full flex items-center justify-between text-gray-400 hover:text-white hover:bg-white/5 px-4 py-2.5 rounded-xl text-sm transition-all">
                <div class="flex items-center gap-3"><i class="fa-solid fa-building-columns w-5 text-center"></i> Kurum & Diğer</div>
                <i id="acc-kurum-icon" class="fa-solid fa-chevron-right text-[10px] opacity-50 transition-transform duration-300"></i>
            </button>
            <div id="acc-kurum" class="pl-11 space-y-1 mt-1 hidden">
                <a href="#" onclick="openMenu(event, 'panel-adres')" class="sub-nav-btn block text-gray-400 hover:text-white text-xs py-2 transition-colors">Açık Adres Sorgu</a>
                <a href="#" onclick="openMenu(event, 'panel-isyeri')" class="sub-nav-btn block text-gray-400 hover:text-white text-xs py-2 transition-colors">İşyeri Bilgisi Sorgu</a>
            </div>

            <div class="pt-5 pb-2 px-4 text-[10px] font-bold text-textMuted uppercase tracking-widest">Yönetim & Destek</div>
            
            <!-- ADMIN PANELİ -->
            <a href="#" id="admin-menu-btn" onclick="openMenu(event, 'panel-admin')" class="nav-btn text-gray-400 hover:text-white hover:bg-white/5 px-4 py-3 rounded-xl text-sm transition-all flex items-center gap-3 hidden">
                <i class="fa-solid fa-user-shield w-5 text-center text-red-500"></i> Admin Paneli
            </a>
            
            <a href="#" onclick="openMenu(event, 'profilim')" class="nav-btn text-gray-400 hover:text-white hover:bg-white/5 px-4 py-3 rounded-xl text-sm transition-all flex items-center gap-3">
                <i class="fa-solid fa-user-gear w-5 text-center"></i> Profil & Ayarlar
            </a>
            
            <button onclick="logout()" class="w-full text-left text-accentDanger hover:text-white hover:bg-accentDanger/10 px-4 py-3 rounded-xl text-sm transition-all flex items-center gap-3 mt-4">
                <i class="fa-solid fa-right-from-bracket w-5 text-center"></i> Çıkış Yap
            </button>
            
        </nav>
        
        <div class="p-4 bg-cardDark/50 border-t border-borderSubtle">
            <div class="flex items-center justify-between text-xs text-textMuted mb-2">
                <span>API Durumu</span>
                <span class="text-accentSuccess font-medium">Aktif</span>
            </div>
            <div class="w-full bg-panelDark rounded-full h-1.5 border border-borderSubtle overflow-hidden">
                <div class="bg-accentSuccess h-1.5 rounded-full" style="width: 98%"></div>
            </div>
        </div>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="flex-1 flex flex-col h-full bg-bgBase relative z-10 overflow-hidden">
        
        <header class="h-20 flex items-center justify-between px-8 bg-panelDark/80 backdrop-blur-xl border-b border-borderSubtle sticky top-0 z-20">
            <div>
                <h2 id="page-title" class="text-xl font-bold text-white tracking-wide">Genel Bakış</h2>
                <p id="page-subtitle" class="text-xs text-textMuted mt-0.5">Sistem istatistikleri ve hızlı erişim</p>
            </div>
            
            <div class="flex items-center gap-5">
                <div class="bg-cardDark border border-borderSubtle px-4 py-2 rounded-xl flex items-center gap-3 text-sm shadow-inner">
                    <div class="w-2.5 h-2.5 bg-accentSuccess rounded-full animate-pulse"></div>
                    <span class="text-white font-medium text-xs tracking-wide">Sistem Güvenli & Aktif</span>
                </div>
                <div class="h-8 w-px bg-borderSubtle"></div>
                <button class="text-textMuted hover:text-white transition-colors relative" onclick="showToast('Yeni bildirim yok', 'info')">
                    <i class="fa-regular fa-bell text-xl"></i>
                    <span class="absolute -top-1 -right-1 w-2.5 h-2.5 bg-accentDanger rounded-full border-2 border-panelDark"></span>
                </button>
            </div>
        </header>

        <div class="flex-1 overflow-y-auto p-8 relative scroll-smooth">
            <div class="max-w-[1600px] mx-auto w-full">

                <!-- 1. DASHBOARD -->
                <div id="dashboard" class="page-content fade-in space-y-8">
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <div class="glass-effect rounded-2xl p-6 relative overflow-hidden group">
                            <div class="absolute -right-6 -top-6 text-accentPrimary/10 group-hover:text-accentPrimary/20 transition-colors duration-500">
                                <i class="fa-solid fa-magnifying-glass text-8xl"></i>
                            </div>
                            <h3 class="text-textMuted text-sm font-medium mb-1 relative z-10">Toplam Sorgu (Senin)</h3>
                            <div class="text-4xl font-black text-white relative z-10" id="stat-user-queries">0</div>
                            <div class="mt-4 flex items-center gap-2 text-xs text-accentSuccess relative z-10 font-medium bg-accentSuccess/10 w-max px-2 py-1 rounded">
                                <i class="fa-solid fa-arrow-trend-up"></i> +12% bu hafta
                            </div>
                        </div>
                        <div class="glass-effect rounded-2xl p-6 relative overflow-hidden group">
                            <div class="absolute -right-6 -top-6 text-accentSuccess/10 group-hover:text-accentSuccess/20 transition-colors duration-500">
                                <i class="fa-solid fa-check-circle text-8xl"></i>
                            </div>
                            <h3 class="text-textMuted text-sm font-medium mb-1 relative z-10">Başarılı Sonuç</h3>
                            <div class="text-4xl font-black text-white relative z-10" id="stat-system-success">0</div>
                            <div class="mt-4 flex items-center gap-2 text-xs text-accentSuccess relative z-10 font-medium bg-accentSuccess/10 w-max px-2 py-1 rounded">
                                <i class="fa-solid fa-bolt"></i> %98.8 Başarı Oranı
                            </div>
                        </div>
                        <div class="glass-effect rounded-2xl p-6 relative overflow-hidden group">
                            <div class="absolute -right-6 -top-6 text-yellow-500/10 group-hover:text-yellow-500/20 transition-colors duration-500">
                                <i class="fa-solid fa-database text-8xl"></i>
                            </div>
                            <h3 class="text-textMuted text-sm font-medium mb-1 relative z-10">Sistem Veritabanı</h3>
                            <div class="text-4xl font-black text-white relative z-10" id="stat-system-db">105M+</div>
                            <div class="mt-4 flex items-center gap-2 text-xs text-yellow-500 relative z-10 font-medium bg-yellow-500/10 w-max px-2 py-1 rounded">
                                <i class="fa-solid fa-clock-rotate-left"></i> Son günc: Bugün 03:00
                            </div>
                        </div>
                        <div class="glass-effect rounded-2xl p-6 relative overflow-hidden group border border-accentPrimary/30 bg-accentPrimary/5">
                            <div class="absolute -right-6 -top-6 text-accentPrimary/10 group-hover:text-accentPrimary/20 transition-colors duration-500 transform rotate-12">
                                <i class="fa-solid fa-crown text-8xl"></i>
                            </div>
                            <h3 class="text-accentPrimary text-sm font-bold mb-1 relative z-10">Plan Durumu</h3>
                            <div class="text-3xl font-black text-white relative z-10 mt-1" id="stat-plan-status">Yükleniyor</div>
                            <div class="mt-4 flex items-center gap-2 text-xs text-white relative z-10 font-medium bg-accentPrimary w-max px-3 py-1 rounded-full shadow-[0_0_10px_rgba(37,99,235,0.5)]">
                                Erişim Aktif
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 2. TC DETAY SORGU -->
                <div id="panel-tc" class="page-content hidden fade-in space-y-6">
                    <div class="bg-cardDark border border-borderSubtle rounded-2xl shadow-xl overflow-hidden">
                        <div class="px-8 py-5 border-b border-borderSubtle bg-panelDark flex justify-between items-center">
                            <div>
                                <h3 class="text-white font-bold">TC Kimlik Detaylı Analiz</h3>
                                <p class="text-xs text-textMuted mt-1">11 haneli kimlik numarası ile sorgulama yapar.</p>
                            </div>
                        </div>
                        <div class="p-8">
                            <div class="max-w-2xl">
                                <div class="flex gap-4">
                                    <input type="text" id="api-tc-input" maxlength="11" placeholder="TC Kimlik No" class="w-full bg-bgBase border-2 border-borderSubtle text-white text-base rounded-xl px-4 py-3.5 focus:outline-none focus:border-accentPrimary transition-colors">
                                    <button onclick="runProxyQuery('tc', {tc: document.getElementById('api-tc-input').value}, 'tc-result', 'tc-raw')" class="bg-accentPrimary hover:bg-accentHover text-white px-8 py-3.5 rounded-xl font-bold flex items-center gap-2 whitespace-nowrap shadow-lg shadow-blue-500/30">
                                        <i class="fa-solid fa-radar"></i> Sorgula
                                    </button>
                                </div>
                            </div>
                            <div id="tc-result" class="hidden mt-10 pt-8 border-t border-borderSubtle space-y-6">
                                <h4 class="text-white font-bold flex items-center gap-2"><i class="fa-solid fa-list-check text-accentSuccess"></i> Analiz Sonucu</h4>
                                <div class="bg-panelDark border border-borderSubtle rounded-xl p-5">
                                    <div id="tc-raw" class="api-raw-box">// Sonuç bekleniyor...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 3. AD SOYAD Kapsamlı -->
                <div id="panel-adsoyad" class="page-content hidden fade-in space-y-6">
                    <div class="bg-cardDark border border-borderSubtle rounded-2xl shadow-xl overflow-hidden">
                        <div class="px-8 py-5 border-b border-borderSubtle bg-panelDark">
                            <h3 class="text-white font-bold">Ad Soyad Kapsamlı Filtreleme</h3>
                        </div>
                        <div class="p-8">
                            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                                <div>
                                    <label class="block text-xs font-medium text-textMuted mb-1.5">Ad * (Zorunlu)</label>
                                    <input type="text" id="ad-input" placeholder="Ad girin..." class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 text-sm outline-none focus:border-accentPrimary">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-textMuted mb-1.5">Soyad</label>
                                    <input type="text" id="soyad-input" placeholder="Soyad..." class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 text-sm outline-none focus:border-accentPrimary">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-textMuted mb-1.5">İl</label>
                                    <input type="text" id="il-input" placeholder="İl..." class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 text-sm outline-none focus:border-accentPrimary">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-textMuted mb-1.5">İlçe</label>
                                    <input type="text" id="ilce-input" placeholder="İlçe..." class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 text-sm outline-none focus:border-accentPrimary">
                                </div>
                                <div class="md:col-span-4 flex justify-end">
                                    <button onclick="runProxyQuery('adsoyad', {ad: document.getElementById('ad-input').value, soyad: document.getElementById('soyad-input').value, il: document.getElementById('il-input').value, ilce: document.getElementById('ilce-input').value}, 'adsoyad-result', 'adsoyad-raw')" class="bg-accentPrimary text-white px-8 py-3 rounded-xl font-bold shadow-lg shadow-blue-500/20">Filtrele & Ara</button>
                                </div>
                            </div>
                            <div id="adsoyad-result" class="hidden mt-8 space-y-4">
                                <div class="bg-panelDark border border-borderSubtle rounded-xl p-5">
                                    <div id="adsoyad-raw" class="api-raw-box">// Sonuç bekleniyor...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 4. AİLE -->
                <div id="panel-aile" class="page-content hidden fade-in space-y-6">
                    <div class="bg-cardDark border border-borderSubtle rounded-2xl shadow-xl overflow-hidden">
                        <div class="px-8 py-5 border-b border-borderSubtle bg-panelDark"><h3 class="text-white font-bold">Aile Sorgu</h3></div>
                        <div class="p-8">
                            <div class="flex gap-4 max-w-2xl">
                                <input type="text" id="aile-input" placeholder="TC Kimlik No" class="flex-1 bg-bgBase border-2 border-borderSubtle text-white rounded-xl px-4 py-3 focus:border-accentPrimary outline-none">
                                <button onclick="runProxyQuery('aile', {tc: document.getElementById('aile-input').value}, 'aile-result', 'aile-raw')" class="bg-accentPrimary text-white px-8 py-3 rounded-xl font-bold">Sorgula</button>
                            </div>
                            <div id="aile-result" class="hidden mt-8 space-y-4">
                                <div class="bg-panelDark border border-borderSubtle rounded-xl p-5">
                                    <div id="aile-raw" class="api-raw-box">// Sonuç bekleniyor...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 5. SÜLALE -->
                <div id="panel-sulale" class="page-content hidden fade-in space-y-6">
                    <div class="bg-cardDark border border-borderSubtle rounded-2xl shadow-xl overflow-hidden">
                        <div class="px-8 py-5 border-b border-borderSubtle bg-panelDark"><h3 class="text-white font-bold">Sülale Sorgu</h3></div>
                        <div class="p-8">
                            <div class="flex gap-4 max-w-2xl">
                                <input type="text" id="sulale-input" placeholder="TC Kimlik No" class="flex-1 bg-bgBase border-2 border-borderSubtle text-white rounded-xl px-4 py-3 focus:border-accentPrimary outline-none">
                                <button onclick="runProxyQuery('sulale', {tc: document.getElementById('sulale-input').value}, 'sulale-result', 'sulale-raw')" class="bg-accentPrimary text-white px-8 py-3 rounded-xl font-bold">Sorgula</button>
                            </div>
                            <div id="sulale-result" class="hidden mt-8 space-y-4">
                                <div class="bg-panelDark border border-borderSubtle rounded-xl p-5">
                                    <div id="sulale-raw" class="api-raw-box">// Sonuç bekleniyor...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 6. ÇOCUK -->
                <div id="panel-cocuk" class="page-content hidden fade-in space-y-6">
                    <div class="bg-cardDark border border-borderSubtle rounded-2xl shadow-xl overflow-hidden">
                        <div class="px-8 py-5 border-b border-borderSubtle bg-panelDark"><h3 class="text-white font-bold">Çocuk Sorgu</h3></div>
                        <div class="p-8">
                            <div class="flex gap-4 max-w-2xl">
                                <input type="text" id="cocuk-input" placeholder="TC Kimlik No" class="flex-1 bg-bgBase border-2 border-borderSubtle text-white rounded-xl px-4 py-3 focus:border-accentPrimary outline-none">
                                <button onclick="runProxyQuery('cocuk', {tc: document.getElementById('cocuk-input').value}, 'cocuk-result', 'cocuk-raw')" class="bg-accentPrimary text-white px-8 py-3 rounded-xl font-bold">Sorgula</button>
                            </div>
                            <div id="cocuk-result" class="hidden mt-8 space-y-4">
                                <div class="bg-panelDark border border-borderSubtle rounded-xl p-5">
                                    <div id="cocuk-raw" class="api-raw-box">// Sonuç bekleniyor...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 7. GSM'DEN TC -->
                <div id="panel-gsmtc" class="page-content hidden fade-in space-y-6">
                    <div class="bg-cardDark border border-borderSubtle rounded-2xl shadow-xl overflow-hidden">
                        <div class="px-8 py-5 border-b border-borderSubtle bg-panelDark"><h3 class="text-white font-bold">GSM'den TC Bulma (gsmtc.php)</h3></div>
                        <div class="p-8">
                            <div class="flex gap-4 max-w-2xl">
                                <input type="text" id="gsmtc-input" placeholder="5XX XXX XX XX" class="flex-1 bg-bgBase border-2 border-borderSubtle text-white rounded-xl px-4 py-3 focus:border-accentPrimary outline-none">
                                <button onclick="runProxyQuery('gsmtc', {gsm: document.getElementById('gsmtc-input').value}, 'gsmtc-result', 'gsmtc-raw')" class="bg-accentPrimary text-white px-8 py-3 rounded-xl font-bold">Sorgula</button>
                            </div>
                            <div id="gsmtc-result" class="hidden mt-8 space-y-4">
                                <div class="bg-panelDark border border-borderSubtle rounded-xl p-5">
                                    <div id="gsmtc-raw" class="api-raw-box">// Sonuç bekleniyor...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 8. TC'DEN GSM -->
                <div id="panel-tcgsm" class="page-content hidden fade-in space-y-6">
                    <div class="bg-cardDark border border-borderSubtle rounded-2xl shadow-xl overflow-hidden">
                        <div class="px-8 py-5 border-b border-borderSubtle bg-panelDark"><h3 class="text-white font-bold">TC'den Üzerine Kayıtlı Hatlar (tcgsm.php)</h3></div>
                        <div class="p-8">
                            <div class="flex gap-4 max-w-2xl">
                                <input type="text" id="tcgsm-input" placeholder="TC Kimlik No" class="flex-1 bg-bgBase border-2 border-borderSubtle text-white rounded-xl px-4 py-3 focus:border-accentPrimary outline-none">
                                <button onclick="runProxyQuery('tcgsm', {tc: document.getElementById('tcgsm-input').value}, 'tcgsm-result', 'tcgsm-raw')" class="bg-accentPrimary text-white px-8 py-3 rounded-xl font-bold">Sorgula</button>
                            </div>
                            <div id="tcgsm-result" class="hidden mt-8 space-y-4">
                                <div class="bg-panelDark border border-borderSubtle rounded-xl p-5">
                                    <div id="tcgsm-raw" class="api-raw-box">// Sonuç bekleniyor...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 9. ADRES -->
                <div id="panel-adres" class="page-content hidden fade-in space-y-6">
                    <div class="bg-cardDark border border-borderSubtle rounded-2xl shadow-xl overflow-hidden">
                        <div class="px-8 py-5 border-b border-borderSubtle bg-panelDark"><h3 class="text-white font-bold">Açık Adres & İkametgah Sorgu</h3></div>
                        <div class="p-8">
                            <div class="flex gap-4 max-w-2xl">
                                <input type="text" id="adres-input" placeholder="TC Kimlik No" class="flex-1 bg-bgBase border-2 border-borderSubtle text-white rounded-xl px-4 py-3 focus:border-accentPrimary outline-none">
                                <button onclick="runProxyQuery('adres', {tc: document.getElementById('adres-input').value}, 'adres-result', 'adres-raw')" class="bg-accentPrimary text-white px-8 py-3 rounded-xl font-bold">Sorgula</button>
                            </div>
                            <div id="adres-result" class="hidden mt-8 space-y-4">
                                <div class="bg-panelDark border border-borderSubtle rounded-xl p-5">
                                    <div id="adres-raw" class="api-raw-box">// Sonuç bekleniyor...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 10. İŞYERİ -->
                <div id="panel-isyeri" class="page-content hidden fade-in space-y-6">
                    <div class="bg-cardDark border border-borderSubtle rounded-2xl shadow-xl overflow-hidden">
                        <div class="px-8 py-5 border-b border-borderSubtle bg-panelDark"><h3 class="text-white font-bold">İşyeri Bilgisi Sorgu (isyeri.php)</h3></div>
                        <div class="p-8">
                            <div class="flex gap-4 max-w-2xl">
                                <input type="text" id="isyeri-input" placeholder="TC Kimlik No" class="flex-1 bg-bgBase border-2 border-borderSubtle text-white rounded-xl px-4 py-3 focus:border-accentPrimary outline-none">
                                <button onclick="runProxyQuery('isyeri', {tc: document.getElementById('isyeri-input').value}, 'isyeri-result', 'isyeri-raw')" class="bg-accentPrimary text-white px-8 py-3 rounded-xl font-bold">Sorgula</button>
                            </div>
                            <div id="isyeri-result" class="hidden mt-8 space-y-4">
                                <div class="bg-panelDark border border-borderSubtle rounded-xl p-5">
                                    <div id="isyeri-raw" class="api-raw-box">// Sonuç bekleniyor...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- ADMIN PANELİ -->
                <div id="panel-admin" class="page-content hidden fade-in space-y-6">
                    <div class="bg-cardDark border border-borderSubtle rounded-2xl shadow-xl overflow-hidden p-8 space-y-6">
                        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-6 border-b border-borderSubtle">
                            <div>
                                <h3 class="text-white font-bold text-xl flex items-center gap-2">
                                    <i class="fa-solid fa-user-shield text-red-500"></i> Yönetim & Yetkilendirme Paneli
                                </h3>
                                <p class="text-xs text-textMuted mt-1">Sisteme kayıtlı üyeleri listeleyin, rollerini güncelleyin veya destek ticket'ı açın.</p>
                            </div>
                            <div class="w-full md:w-72">
                                <input type="text" id="admin-search-input" onkeyup="filterAdminMembers()" placeholder="Üye ara (Ad veya Rol)..." class="w-full bg-bgBase border border-borderSubtle text-white text-sm rounded-xl px-4 py-2.5 outline-none focus:border-accentPrimary">
                            </div>
                        </div>

                        <div class="overflow-x-auto">
                            <table class="w-full text-left border-collapse" id="admin-members-table">
                                <thead>
                                    <tr class="border-b border-borderSubtle text-textMuted text-xs uppercase tracking-wider">
                                        <th class="py-3 px-4">Kullanıcı Adı</th>
                                        <th class="py-3 px-4">Mevcut Rol</th>
                                        <th class="py-3 px-4">Kayıt Tarihi</th>
                                        <th class="py-3 px-4 text-right">İşlemler (Rol Ver / Mesaj At)</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-borderSubtle text-sm" id="admin-members-tbody">
                                    <tr>
                                        <td colspan="4" class="py-10 text-center text-textMuted font-medium">
                                            <i class="fa-solid fa-circle-notch fa-spin mr-2 text-accentPrimary"></i> Veriler Python sunucusundan çekiliyor...
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- PROFILE -->
                <div id="profilim" class="page-content hidden fade-in space-y-6">
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        
                        <div class="bg-cardDark border border-borderSubtle rounded-2xl p-6 shadow-xl flex flex-col items-center text-center">
                            <div class="relative mb-4">
                                <img id="profile-avatar" src="https://ui-avatars.com/api/?name=User&background=2563eb&color=fff&size=128" alt="Profil" class="w-24 h-24 rounded-2xl border-2 border-borderSubtle shadow-lg">
                                <div class="absolute -bottom-1 -right-1 w-5 h-5 bg-accentSuccess border-2 border-panelDark rounded-full"></div>
                            </div>
                            <h3 class="text-white font-bold text-lg" id="profile-display-name">Yükleniyor...</h3>
                            <p class="text-xs text-textMuted mt-0.5" id="profile-role-title">Bağlanıyor</p>
                            <div class="mt-6 w-full pt-6 border-t border-borderSubtle space-y-3 text-left text-xs">
                                <div class="flex justify-between text-textMuted">
                                    <span>Kayıt Tarihi:</span>
                                    <span class="text-white font-medium" id="profile-date">01.06.2026</span>
                                </div>
                                <div class="flex justify-between text-textMuted">
                                    <span>Toplam Sorgu:</span>
                                    <span class="text-white font-medium" id="profile-queries">0</span>
                                </div>
                                <div class="flex justify-between text-textMuted">
                                    <span>Yetki Seviyesi:</span>
                                    <span class="text-accentPrimary font-bold" id="profile-auth-level">Standart Yetki</span>
                                </div>
                            </div>
                        </div>

                        <div class="lg:col-span-2 space-y-6">
                            <div class="bg-cardDark border border-borderSubtle rounded-2xl p-6 shadow-xl">
                                <h4 class="text-white font-bold text-base mb-1 flex items-center gap-2">
                                    <i class="fa-solid fa-user-pen text-accentPrimary"></i> Kullanıcı Adı Değiştir
                                </h4>
                                <p class="text-xs text-textMuted mb-5">Sistemde görünecek yeni adınızı belirleyin.</p>
                                
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-xs font-medium text-textMuted mb-2">Yeni Kullanıcı Adı</label>
                                        <input type="text" id="new-username-input" placeholder="Yeni kullanıcı adı giriniz..." class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 focus:border-accentPrimary outline-none text-sm">
                                    </div>
                                    <div class="flex justify-end">
                                        <button onclick="handleUsernameChange()" class="bg-accentPrimary hover:bg-accentHover text-white px-6 py-2.5 rounded-xl text-sm font-bold transition-all shadow-lg shadow-blue-500/20">
                                            Adı Güncelle
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div class="bg-cardDark border border-borderSubtle rounded-2xl p-6 shadow-xl">
                                <h4 class="text-white font-bold text-base mb-1 flex items-center gap-2">
                                    <i class="fa-solid fa-envelope-circle-check text-accentSuccess"></i> E-Posta Adresi Değiştir
                                </h4>
                                <p class="text-xs text-textMuted mb-5">Güvenliğiniz için mevcut şifrenizi girmeniz gerekmektedir.</p>
                                
                                <div class="space-y-4">
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                            <label class="block text-xs font-medium text-textMuted mb-2">Yeni E-Posta Adresi</label>
                                            <input type="email" id="new-email-input" placeholder="ornek@mail.com" class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 focus:border-accentPrimary outline-none text-sm">
                                        </div>
                                        <div>
                                            <label class="block text-xs font-medium text-textMuted mb-2">Mevcut Şifreniz</label>
                                            <input type="password" id="current-password-input" placeholder="••••••••" class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl px-4 py-3 focus:border-accentPrimary outline-none text-sm">
                                        </div>
                                    </div>
                                    <div class="flex justify-end">
                                        <button onclick="handleEmailChange()" class="bg-accentSuccess hover:bg-emerald-700 text-white px-6 py-2.5 rounded-xl text-sm font-bold transition-all shadow-lg shadow-emerald-600/20">
                                            E-Postayı Güncelle
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </main>

    <!-- ROL VERME MODALI -->
    <div id="role-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm hidden fade-in">
        <div class="bg-panelDark border border-borderSubtle w-full max-w-md rounded-2xl p-6 shadow-2xl space-y-5">
            <div class="flex justify-between items-center">
                <h3 class="text-white font-bold text-base flex items-center gap-2">
                    <i class="fa-solid fa-shield-halved text-accentPrimary"></i> Üyeye Rol Ata: <span id="modal-username-text" class="text-accentPrimary"></span>
                </h3>
                <button onclick="closeRoleModal()" class="text-textMuted hover:text-white"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>
            
            <div class="space-y-2">
                <label class="flex items-center gap-3 p-3 bg-cardDark border border-borderSubtle rounded-xl cursor-pointer hover:border-accentPrimary transition-colors">
                    <input type="radio" name="selected-role" value="Admin" class="accent-blue-600">
                    <div><span class="text-red-500 font-semibold text-sm">Admin (Yönetici)</span></div>
                </label>
                <label class="flex items-center gap-3 p-3 bg-cardDark border border-borderSubtle rounded-xl cursor-pointer hover:border-accentPrimary transition-colors">
                    <input type="radio" name="selected-role" value="Kurucu" class="accent-blue-600">
                    <div><span class="text-orange-400 font-semibold text-sm">Kurucu</span></div>
                </label>
                <label class="flex items-center gap-3 p-3 bg-cardDark border border-borderSubtle rounded-xl cursor-pointer hover:border-accentPrimary transition-colors">
                    <input type="radio" name="selected-role" value="VIP" class="accent-blue-600">
                    <div><span class="text-purple-400 font-semibold text-sm">VIP Üye</span></div>
                </label>
                <label class="flex items-center gap-3 p-3 bg-cardDark border border-borderSubtle rounded-xl cursor-pointer hover:border-accentPrimary transition-colors">
                    <input type="radio" name="selected-role" value="Member" class="accent-blue-600">
                    <div><span class="text-blue-400 font-semibold text-sm">Member (Standart Üye)</span></div>
                </label>
            </div>

            <div class="flex justify-end gap-3 pt-3 border-t border-borderSubtle">
                <button onclick="closeRoleModal()" class="px-4 py-2 rounded-xl text-xs font-semibold bg-cardDark text-textMuted hover:text-white">İptal</button>
                <button onclick="submitRoleChange()" class="px-5 py-2 rounded-xl text-xs font-bold bg-accentPrimary text-white hover:bg-accentHover">Rolü Güncelle</button>
            </div>
        </div>
    </div>

    <!-- TICKET / MESAJ MODALI -->
    <div id="ticket-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm hidden fade-in">
        <div class="bg-panelDark border border-borderSubtle w-full max-w-lg rounded-2xl p-6 shadow-2xl space-y-5">
            <div class="flex justify-between items-center">
                <h3 class="text-white font-bold text-base flex items-center gap-2">
                    <i class="fa-solid fa-headset text-accentSuccess"></i> Destek Ticket Mesajı: <span id="ticket-username-text" class="text-accentSuccess"></span>
                </h3>
                <button onclick="closeTicketModal()" class="text-textMuted hover:text-white"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>
            
            <div class="bg-cardDark border border-borderSubtle rounded-xl p-4 h-48 overflow-y-auto space-y-3 text-xs" id="ticket-messages-box">
                <div class="text-textMuted text-center italic py-4">Ticket geçmişi başlatıldı. Üyeye doğrudan mesaj iletebilir veya çözüldüğünde kapatabilirsiniz.</div>
            </div>

            <div class="space-y-3">
                <textarea id="ticket-reply-input" rows="2" placeholder="Üyeye mesajınızı yazın..." class="w-full bg-bgBase border border-borderSubtle text-white rounded-xl p-3 text-xs outline-none focus:border-accentPrimary resize-none"></textarea>
                <div class="flex justify-between items-center">
                    <button onclick="closeTicketSession()" class="bg-accentDanger/10 text-accentDanger hover:bg-accentDanger hover:text-white px-4 py-2 rounded-xl text-xs font-bold transition-all">
                        <i class="fa-solid fa-lock"></i> Ticket'ı Kapat
                    </button>
                    <button onclick="sendTicketMessage()" class="bg-accentSuccess hover:bg-emerald-700 text-white px-6 py-2 rounded-xl text-xs font-bold transition-all">
                        Gönder
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_URL = "https://eropanel.onrender.com/api";
        
        let currentUser = JSON.parse(localStorage.getItem('eropanel_current_user'));
        if (!currentUser) {
            window.location.href = '/'; 
        }

        let currentUserRole = currentUser ? currentUser.role : 'Member'; 
        let targetUserForRole = '';
        let targetUserForTicket = '';

        window.addEventListener('DOMContentLoaded', async () => {
            try {
                const res = await fetch(`${API_URL}/users`);
                const data = await res.json();
                if(data.success) {
                    const fresh = data.users.find(u => u.username.toLowerCase() === currentUser.username.toLowerCase());
                    if(fresh) {
                        currentUser = fresh;
                        currentUserRole = fresh.role;
                        localStorage.setItem('eropanel_current_user', JSON.stringify(currentUser));
                    }
                }
            } catch(e) {}

            if (currentUser) {
                const avatarUrl = `https://ui-avatars.com/api/?name=${currentUser.username}&background=2563eb&color=fff`;
                
                document.getElementById('sidebar-display-name').innerText = currentUser.username;
                document.getElementById('sidebar-role-badge').innerText = currentUser.role;
                document.getElementById('sidebar-avatar').src = avatarUrl;
                
                const profileDisplay = document.getElementById('profile-display-name');
                if(profileDisplay) profileDisplay.innerText = currentUser.username;
                
                const profileRole = document.getElementById('profile-role-title');
                if(profileRole) profileRole.innerText = currentUser.role;
                
                const profileAuth = document.getElementById('profile-auth-level');
                if(profileAuth) profileAuth.innerText = `${currentUser.role} (Yetkili)`;
                
                const profileAvatar = document.getElementById('profile-avatar');
                if(profileAvatar) profileAvatar.src = avatarUrl;

                document.getElementById('profile-date').innerText = currentUser.date || '01.06.2026';
                document.getElementById('stat-plan-status').innerText = currentUser.role;
            }

            const adminBtn = document.getElementById('admin-menu-btn');
            if (['founder', 'admin', 'kurucu'].includes(currentUserRole.toLowerCase())) {
                if (adminBtn) adminBtn.classList.remove('hidden');
            }
            
            loadDashboardData();
        });

        function logout() {
            localStorage.removeItem('eropanel_current_user');
            window.location.href = '/';
        }

        async function loadDashboardData() {
            try {
                const statsRes = await fetch(`${API_URL}/stats`);
                const statsData = await statsRes.json();
                if (statsData.success) {
                    document.getElementById('stat-user-queries').innerText = currentUser.queries_count || '0';
                    document.getElementById('stat-system-success').innerText = (statsData.successful_queries || 4812).toLocaleString('tr-TR');
                    document.getElementById('stat-system-db').innerText = statsData.database_records || '105M+';
                    document.getElementById('profile-queries').innerText = currentUser.queries_count || '0';
                }
                
                if (['founder', 'admin', 'kurucu'].includes(currentUserRole.toLowerCase())) {
                    const usersRes = await fetch(`${API_URL}/users`);
                    const usersData = await usersRes.json();
                    
                    const tbody = document.getElementById('admin-members-tbody');
                    if (usersData.success && tbody) {
                        tbody.innerHTML = '';
                        const reversedUsers = [...usersData.users].reverse();

                        reversedUsers.forEach(user => {
                            let badgeColor = user.role.toLowerCase() === 'founder' ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/30' : 
                                             user.role.toLowerCase() === 'admin' ? 'bg-red-500/10 text-red-500 border-red-500/30' : 
                                             user.role.toLowerCase() === 'kurucu' ? 'bg-orange-500/10 text-orange-400 border-orange-500/30' :
                                             user.role.toLowerCase() === 'vip' ? 'bg-purple-500/10 text-purple-400 border-purple-500/30' :
                                             'bg-blue-500/10 text-blue-400 border-blue-500/30';

                            tbody.innerHTML += `
                                <tr class="hover:bg-white/5 transition-colors" data-username="${user.username}">
                                    <td class="py-4 px-4 font-semibold text-white flex items-center gap-2">
                                        <img src="https://ui-avatars.com/api/?name=${user.username}&background=2563eb&color=fff" class="w-7 h-7 rounded-lg"> ${user.username}
                                    </td>
                                    <td class="py-4 px-4">
                                        <span class="px-2.5 py-1 ${badgeColor} rounded-full text-xs font-bold">${user.role}</span>
                                    </td>
                                    <td class="py-4 px-4 text-textMuted text-xs">${user.date}</td>
                                    <td class="py-4 px-4 text-right space-x-2">
                                        ${user.role.toLowerCase() !== 'founder' ? `<button onclick="openRoleModal('${user.username}')" class="bg-cardDark border border-borderSubtle hover:bg-accentPrimary hover:text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors">Rol Ver</button>` : '<span class="text-xs text-yellow-500 font-bold">Founder</span>'}
                                        <button onclick="openTicketModal('${user.username}')" class="bg-accentPrimary/10 text-accentPrimary hover:bg-accentPrimary hover:text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors">Mesaj Gönder</button>
                                    </td>
                                </tr>
                            `;
                        });
                    }
                }
            } catch (error) {
                console.error("Veriler çekilemedi:", error);
            }
        }

        const pageTitles = {
            'dashboard': { title: 'Genel Bakış', subtitle: 'Sistem istatistikleri ve hızlı erişim' },
            'panel-tc': { title: 'TC Detay Sorgu', subtitle: 'Mernis 2026 Altyapısı' },
            'panel-adsoyad': { title: 'Ad Soyad Filtreleme', subtitle: 'Kapsamlı daraltma ve arama aracı' },
            'panel-aile': { title: 'Aile Sorgu', subtitle: 'Aile bağı sorgulama' },
            'panel-sulale': { title: 'Sülale Sorgu', subtitle: 'Genişletilmiş sülale sorgulama' },
            'panel-cocuk': { title: 'Çocuk Sorgu', subtitle: 'Çocuk bilgisi sorgulama' },
            'panel-gsmtc': { title: "GSM'den TC", subtitle: "GSM numarasından kimlik bulma" },
            'panel-tcgsm': { title: "TC'den GSM", subtitle: "Kimlik numarasına bağlı tüm hatlar" },
            'panel-adres': { title: 'Adres Çözümleri', subtitle: 'Açık ikametgah kayıtları' },
            'panel-isyeri': { title: 'İşyeri Bilgisi', subtitle: 'SGK ve kurum işyeri kayıtları' },
            'panel-admin': { title: 'Admin & Yetkilendirme', subtitle: 'Üye yönetimi, roller ve ticket sistemi' },
            'profilim': { title: 'Profil & Ayarlar', subtitle: 'Hesap tercihleri ve loglar' }
        };

        function openMenu(event, pageId) {
            if(event) event.preventDefault();
            
            if(pageId === 'panel-admin' && !['founder', 'admin', 'kurucu'].includes(currentUserRole.toLowerCase())) {
                showToast('Bu alana erişim yetkiniz yok!', 'error');
                return;
            }

            document.querySelectorAll('.page-content').forEach(el => {
                el.classList.add('hidden');
                el.classList.remove('fade-in');
            });
            
            const target = document.getElementById(pageId);
            if(target) {
                target.classList.remove('hidden');
                void target.offsetWidth; 
                target.classList.add('fade-in');
            }
            
            if(pageTitles[pageId]) {
                document.getElementById('page-title').innerText = pageTitles[pageId].title;
                document.getElementById('page-subtitle').innerText = pageTitles[pageId].subtitle;
            }

            document.querySelectorAll('.nav-btn').forEach(el => {
                el.classList.remove('active', 'bg-accentPrimary/10', 'text-accentPrimary', 'border-accentPrimary/30');
                el.classList.add('text-gray-400', 'border-transparent');
            });
            document.querySelectorAll('.sub-nav-btn').forEach(el => {
                el.classList.remove('text-accentPrimary', 'font-bold');
                el.classList.add('text-gray-400');
            });
            
            if(event) {
                let btn = event.currentTarget;
                if(btn.classList.contains('nav-btn')) {
                    btn.classList.remove('text-gray-400', 'border-transparent');
                    btn.classList.add('active', 'bg-accentPrimary/10', 'text-accentPrimary', 'border-accentPrimary/30');
                } else if(btn.classList.contains('sub-nav-btn')) {
                    btn.classList.remove('text-gray-400');
                    btn.classList.add('text-accentPrimary', 'font-bold');
                }
            }
        }

        function toggleAccordion(id) {
            const el = document.getElementById(id);
            const icon = document.getElementById(id + '-icon');
            if(el.classList.contains('hidden')) {
                el.classList.remove('hidden');
                icon.classList.add('rotate-90');
            } else {
                el.classList.add('hidden');
                icon.classList.remove('rotate-90');
            }
        }

        function showToast(message, type = 'success') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            let colorClass = 'border-accentSuccess text-accentSuccess';
            let icon = 'fa-check-circle';
            if(type === 'warning') { colorClass = 'border-yellow-500 text-yellow-500'; icon = 'fa-triangle-exclamation'; }
            if(type === 'error') { colorClass = 'border-accentDanger text-accentDanger'; icon = 'fa-circle-xmark'; }
            if(type === 'info') { colorClass = 'border-accentPrimary text-accentPrimary'; icon = 'fa-info-circle'; }
            
            toast.className = `bg-panelDark border ${colorClass} shadow-[0_5px_15px_rgba(0,0,0,0.5)] rounded-lg px-4 py-3 flex items-center gap-3 transform transition-all duration-300 translate-x-full opacity-0`;
            toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span class="text-sm font-medium text-white">${message}</span>`;
            
            container.appendChild(toast);
            requestAnimationFrame(() => toast.classList.remove('translate-x-full', 'opacity-0'));
            setTimeout(() => {
                toast.classList.add('translate-x-full', 'opacity-0');
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }

        function filterAdminMembers() {
            const query = document.getElementById('admin-search-input').value.toLowerCase();
            const rows = document.querySelectorAll('#admin-members-table tbody tr');
            rows.forEach(row => {
                const username = row.getAttribute('data-username');
                if(username && username.toLowerCase().includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        function openRoleModal(username) {
            targetUserForRole = username;
            document.getElementById('modal-username-text').innerText = username;
            document.getElementById('role-modal').classList.remove('hidden');
        }

        function closeRoleModal() {
            document.getElementById('role-modal').classList.add('hidden');
        }

        async function submitRoleChange() {
            const selectedRadio = document.querySelector('input[name="selected-role"]:checked');
            if(!selectedRadio) {
                showToast('Lütfen bir rol seçiniz!', 'warning');
                return;
            }
            const newRole = selectedRadio.value;

            try {
                const res = await fetch(`${API_URL}/update-role`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ username: targetUserForRole, role: newRole })
                });
                const data = await res.json();
                
                if(res.ok) {
                    showToast(`${targetUserForRole} kullanıcısına '${newRole}' rolü başarıyla verildi!`, 'success');
                    closeRoleModal();
                    loadDashboardData();
                } else {
                    showToast(data.error || 'İşlem başarısız!', 'error');
                }
            } catch (err) {
                showToast('Sunucu bağlantı hatası!', 'error');
            }
        }

        function openTicketModal(username) {
            targetUserForTicket = username;
            document.getElementById('ticket-username-text').innerText = username;
            document.getElementById('ticket-messages-box').innerHTML = `
                <div class="p-2.5 bg-bgBase rounded-xl border border-borderSubtle">
                    <span class="text-accentPrimary font-bold">Sistem:</span> ${username} ile destek oturumu başlatıldı.
                </div>
            `;
            document.getElementById('ticket-modal').classList.remove('hidden');
        }

        function closeTicketModal() {
            document.getElementById('ticket-modal').classList.add('hidden');
        }

        function sendTicketMessage() {
            const input = document.getElementById('ticket-reply-input');
            const msg = input.value.trim();
            if(!msg) return;

            const box = document.getElementById('ticket-messages-box');
            box.innerHTML += `
                <div class="p-2.5 bg-accentPrimary/10 border border-accentPrimary/30 rounded-xl text-right">
                    <span class="text-accentPrimary font-bold">Admin:</span> ${msg}
                </div>
            `;
            input.value = '';
            box.scrollTop = box.scrollHeight;
            showToast('Mesaj üyeye iletildi', 'success');
        }

        function closeTicketSession() {
            showToast('Ticket oturumu kapatıldı.', 'info');
            closeTicketModal();
        }

        function handleUsernameChange() {
            const inputField = document.getElementById('new-username-input');
            const newName = inputField.value.trim();

            if (!newName) {
                showToast('Kullanıcı adı boş olamaz!', 'error');
                return;
            }

            document.getElementById('profile-display-name').innerText = newName;
            document.getElementById('sidebar-display-name').innerText = newName;
            
            const newAvatarUrl = `https://ui-avatars.com/api/?name=${newName}&background=2563eb&color=fff`;
            document.getElementById('sidebar-avatar').src = newAvatarUrl;
            document.getElementById('profile-avatar').src = newAvatarUrl;

            showToast('Kullanıcı adı başarıyla değiştirildi!', 'success');
            inputField.value = '';
        }

        function handleEmailChange() {
            const newEmail = document.getElementById('new-email-input').value.trim();
            const currentPassword = document.getElementById('current-password-input').value.trim();

            if (!newEmail || !currentPassword) {
                showToast('Lütfen tüm alanları doldurun!', 'warning');
                return;
            }

            if (!newEmail.includes('@')) {
                showToast('Geçerli bir e-posta adresi giriniz!', 'error');
                return;
            }

            showToast('E-posta adresi başarıyla güncellendi!', 'success');
            document.getElementById('new-email-input').value = '';
            document.getElementById('current-password-input').value = '';
        }

        async function runProxyQuery(endpoint, params, resultId, rawOutputId) {
            const btn = event.currentTarget;
            const originalText = btn.innerHTML;
            btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> İşleniyor...`;
            btn.disabled = true;
            btn.classList.add('opacity-80');
            
            document.getElementById(resultId).classList.add('hidden');
            const rawBox = document.getElementById(rawOutputId);
            rawBox.innerText = 'Python API sunucusundan veri çekiliyor...';

            const queryString = new URLSearchParams(params).toString();

            try {
                const response = await fetch(`${API_URL}/${endpoint}?${queryString}`);
                const jsonData = await response.json();
                
                if (!response.ok || !jsonData.success) {
                    throw new Error(jsonData.error || `HTTP Hata: ${response.status}`);
                }

                rawBox.innerText = JSON.stringify(jsonData.data, null, 2);
                document.getElementById(resultId).classList.remove('hidden');
                document.getElementById(resultId).classList.add('fade-in');
                
                currentUser.queries_count = (currentUser.queries_count || 0) + 1;
                document.getElementById('stat-user-queries').innerText = currentUser.queries_count;
                document.getElementById('profile-queries').innerText = currentUser.queries_count;
                localStorage.setItem('eropanel_current_user', JSON.stringify(currentUser));

                showToast('İşlem başarılı!', 'success');
            } catch (error) {
                console.error(error);
                rawBox.innerText = `[BAĞLANTI VEYA API HATASI]\nDetay: ${error.message}`;
                document.getElementById(resultId).classList.remove('hidden');
                document.getElementById(resultId).classList.add('fade-in');
                showToast(error.message || 'İşlem Başarısız!', 'error');
            } finally {
                btn.innerHTML = originalText;
                btn.disabled = false;
                btn.classList.remove('opacity-80');
            }
        }
    </script>
</body>
</html>
"""

# --- FLASK ENDPOINT TANIMLARI ---

@app.route('/')
def home():
    return render_template_string(LOGIN_PAGE_HTML)

@app.route('/panel')
def panel():
    return render_template_string(PANEL_PAGE_HTML)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    login_input = data.get('username', '').strip().lower()
    password = data.get('password', '').strip()

    if not login_input or not password:
        return jsonify({"success": False, "error": "Kullanıcı adı/Gmail ve şifre zorunludur!"}), 400

    user = next((u for u in users_db if (u["username"].lower() == login_input or u["email"].lower() == login_input) and u["password"] == password), None)
    if not user:
        return jsonify({"success": False, "error": "Kullanıcı adı/Gmail veya şifre hatalı!"}), 401

    return jsonify({"success": True, "message": "Giriş başarılı!", "user": user})

@app.route('/api/send-code', methods=['POST'])
def send_code():
    data = request.json
    email = data.get('email', '').strip()
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

    message = MIMEMultipart("alternative")
    message["Subject"] = "EROPANEL - Hesap Dogrulama Kodu"
    message["From"] = sender_email
    message["To"] = email

    html = f"""
    <div style="background-color: #0a0f1c; color: #f3f4f6; padding: 30px; font-family: sans-serif; border-radius: 12px; border: 1px solid #374151;">
        <h2 style="color: #dc2626; margin-top: 0;">EROPANEL Guvenlik Merkezi</h2>
        <p>Eropanel hesabinizi dogrulamak icin talep ettiginiz onay kodu:</p>
        <div style="background: #111827; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
            <span style="color: #2563eb; font-size: 28px; font-weight: bold; letter-spacing: 6px;">{code}</span>
        </div>
        <p style="font-size: 12px; color: #9ca3af;">Bu kodu kimseyle paylasmayin.</p>
    </div>
    """
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        return jsonify({"success": True, "message": "Kod basariyla Gmail adresine gonderildi."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/verify-and-register', methods=['POST'])
def verify_and_register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    code = data.get('code')

    if verification_codes.get(email) != code:
        return jsonify({"success": False, "error": "Hatali veya suresi dolmus onay kodu!"}), 400

    new_user = {
        "username": username,
        "email": email,
        "password": password,
        "role": "Member",
        "date": datetime.datetime.now().strftime("%d.%m.%Y"),
        "queries_count": 0
    }
    users_db.append(new_user)
    del verification_codes[email]
    return jsonify({"success": True, "message": "Kayit basariyla tamamlandi!"})

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({"success": True, "users": users_db})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_queries = sum(u.get("queries_count", 0) for u in users_db) + system_stats["total_queries"]
    return jsonify({
        "success": True,
        "total_users": len(users_db),
        "total_queries": total_queries,
        "successful_queries": system_stats["successful_queries"] + sum(u.get("queries_count", 0) for u in users_db),
        "database_records": system_stats["database_records"]
    })

@app.route('/api/update-role', methods=['POST'])
def update_role():
    data = request.json
    username = data.get('username')
    new_role = data.get('role')

    user = next((u for u in users_db if u["username"].lower() == username.lower()), None)
    if not user:
        return jsonify({"success": False, "error": "Kullanici bulunamadi!"}), 404

    user["role"] = new_role
    return jsonify({"success": True, "message": f"{username} rolü {new_role} olarak güncellendi."})

# --- PROXY ENDPOINTLERİ ---
@app.route('/api/tc', methods=['GET'])
def api_tc():
    tc = request.args.get('tc')
    if not tc or len(tc) != 11:
        return jsonify({"success": False, "error": "Geçersiz TC"}), 400
    try:
        response = requests.get(f"http://arastir.vip/api/tc.php?tc={tc}", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                data = {"raw_response": response.text}
            if data:
                return jsonify({"success": True, "data": data}), 200
        return jsonify({"success": False, "error": "Kayıt bulunamadı"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": "Sunucu hatası"}), 500

@app.route('/api/adsoyad', methods=['GET'])
def api_adsoyad():
    ad = request.args.get('ad', '')
    soyad = request.args.get('soyad', '')
    il = request.args.get('il', '')
    ilce = request.args.get('ilce', '')
    
    if not ad:
        return jsonify({"success": False, "error": "Geçersiz parametre"}), 400
        
    try:
        response = requests.get(f"http://arastir.vip/api/adsoyad.php?ad={ad}&soyad={soyad}&il={il}&ilce={ilce}", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                data = {"raw_response": response.text}
            if data:
                return jsonify({"success": True, "data": data}), 200
        return jsonify({"success": False, "error": "Kayıt bulunamadı"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": "Sunucu hatası"}), 500

@app.route('/api/aile', methods=['GET'])
def api_aile():
    tc = request.args.get('tc', '')
    if not tc or len(tc) != 11:
        return jsonify({"success": False, "error": "Geçersiz TC"}), 400
    try:
        response = requests.get(f"http://arastir.vip/api/aile.php?tc={tc}", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                data = {"raw_response": response.text}
            if data:
                return jsonify({"success": True, "data": data}), 200
        return jsonify({"success": False, "error": "Kayıt bulunamadı"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": "Sunucu hatası"}), 500

@app.route('/api/sulale', methods=['GET'])
def api_sulale():
    tc = request.args.get('tc', '')
    if not tc or len(tc) != 11:
        return jsonify({"success": False, "error": "Geçersiz TC"}), 400
    try:
        response = requests.get(f"http://arastir.vip/api/sulale.php?tc={tc}", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                data = {"raw_response": response.text}
            if data:
                return jsonify({"success": True, "data": data}), 200
        return jsonify({"success": False, "error": "Kayıt bulunamadı"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": "Sunucu hatası"}), 500

@app.route('/api/cocuk', methods=['GET'])
def api_cocuk():
    tc = request.args.get('tc', '')
    if not tc or len(tc) != 11:
        return jsonify({"success": False, "error": "Geçersiz TC"}), 400
    try:
        response = requests.get(f"http://arastir.vip/api/cocuk.php?tc={tc}", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                data = {"raw_response": response.text}
            if data:
                return jsonify({"success": True, "data": data}), 200
        return jsonify({"success": False, "error": "Kayıt bulunamadı"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": "Sunucu hatası"}), 500

@app.route('/api/adres', methods=['GET'])
def api_adres():
    tc = request.args.get('tc', '')
    if not tc or len(tc) != 11:
        return jsonify({"success": False, "error": "Geçersiz TC"}), 400
    try:
        response = requests.get(f"http://arastir.vip/api/adres.php?tc={tc}", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                data = {"raw_response": response.text}
            if data:
                return jsonify({"success": True, "data": data}), 200
        return jsonify({"success": False, "error": "Kayıt bulunamadı"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": "Sunucu hatası"}), 500

@app.route('/api/gsmtc', methods=['GET'])
def api_gsmtc():
    gsm = request.args.get('gsm', '')
    if not gsm:
        return jsonify({"success": False, "error": "Geçersiz parametre"}), 400
    try:
        response = requests.get(f"http://arastir.vip/api/gsmtc.php?gsm={gsm}", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                data = {"raw_response": response.text}
            if data:
                return jsonify({"success": True, "data": data}), 200
        return jsonify({"success": False, "error": "Kayıt bulunamadı"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": "Sunucu hatası"}), 500

@app.route('/api/tcgsm', methods=['GET'])
def api_tcgsm():
    tc = request.args.get('tc', '')
    if not tc or len(tc) != 11:
        return jsonify({"success": False, "error": "Geçersiz TC"}), 400
    try:
        response = requests.get(f"http://arastir.vip/api/tcgsm.php?tc={tc}", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                data = {"raw_response": response.text}
            if data:
                return jsonify({"success": True, "data": data}), 200
        return jsonify({"success": False, "error": "Kayıt bulunamadı"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": "Sunucu hatası"}), 500

@app.route('/api/isyeri', methods=['GET'])
def api_isyeri():
    tc = request.args.get('tc', '')
    if not tc or len(tc) != 11:
        return jsonify({"success": False, "error": "Geçersiz TC"}), 400
    try:
        response = requests.get(f"http://arastir.vip/api/isyeri.php?tc={tc}", timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                data = {"raw_response": response.text}
            if data:
                return jsonify({"success": True, "data": data}), 200
        return jsonify({"success": False, "error": "Kayıt bulunamadı"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": "Sunucu hatası"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Python Sunucusu Çalışıyor: port {port}")
    app.run(host='0.0.0.0', port=port)
