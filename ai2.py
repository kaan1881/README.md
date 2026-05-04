import urllib.parse
import requests
import pyttsx3
import speech_recognition as sr
import threading
import tkinter as tk
from tkinter import scrolledtext
import json
import os
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

motor = pyttsx3.init()
motor.setProperty('rate', 180)
motor.setProperty('volume', 1.0)

HAFIZA_DOSYASI = "hafiza.json"

def konus(metin):
    try:
        motor.say(metin)
        motor.runAndWait()
    except:
        pass

r = sr.Recognizer()

def hafiza_yukle():
    if os.path.exists(HAFIZA_DOSYASI):
        try:
            with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def hafiza_kaydet(gecmis_listesi):
    try:
        with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(gecmis_listesi, f, ensure_ascii=False, indent=4)
    except:
        pass

gecmis = hafiza_yukle()
sesli_mod_aktif = False

def dinle():
    with sr.Microphone() as kaynak:
        r.pause_threshold = 0.8
        r.adjust_for_ambient_noise(kaynak, duration=0.5)
        try:
            print("Dinliyorum...")
            ses = r.listen(kaynak, timeout=5, phrase_time_limit=10)
            return r.recognize_google(ses, language='tr-TR')
        except:
            return None

def yapay_zeka_sor(soru):
    global gecmis

    sistem_mesaji = "Senin adın kaanGemini. Kurucun Kaan'dır. Kaan'a ismiyle hitap et. Samimi ol."

    baglam = "\n".join(gecmis[-1:]) if gecmis else ""
    tam_soru = f"{sistem_mesaji}\n{baglam}\nKaan: {soru}"

    encoded_soru = urllib.parse.quote(tam_soru)
    url = f"https://text.pollinations.ai/{encoded_soru}?model=openai&cache=false"

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}

        yanit = requests.get(url, headers=headers, timeout=35, verify=False)

        if yanit.status_code == 429:
            return "Kaan, sunucu şu an çok yoğun. Lütfen birkaç saniye sonra tekrar sor."

        if yanit.status_code == 200:
            cevap = yanit.text

            gecmis.append(f"Kaan: {soru}")
            gecmis.append(f"Kaanai: {cevap}")

            if len(gecmis) > 6:
                gecmis = gecmis[-4:]

            hafiza_kaydet(gecmis)
            return cevap
        else:
            return f"Bağlantıda bir sorun var Kaan. (Hata: {yanit.status_code})"

    except requests.exceptions.Timeout:
        return "Sunucu şu an çok yavaş Kaan, tekrar denememi ister misin?"
    except Exception as e:
        print(f"HATA: {e}")
        return "Küçük bir teknik hata oluştu."

def ekrana_yaz(kisi, mesaj):
    chat.config(state=tk.NORMAL)
    chat.insert(tk.END, f"\n{kisi}: ", "bold")
    chat.insert(tk.END, f"{mesaj}\n")
    chat.tag_configure("bold", font=("Segoe UI", 10, "bold"))
    chat.config(state=tk.DISABLED)
    chat.see(tk.END)

def gonder(event=None):
    soru = entry.get()
    if not soru: return

    entry.delete(0, tk.END)
    ekrana_yaz("Kaan", soru)

    def islem():
        cevap = yapay_zeka_sor(soru)
        ekrana_yaz("KAANGemini", cevap)
        konus(cevap)

    threading.Thread(target=islem, daemon=True).start()

def sesli_mod_dongusu():
    global sesli_mod_aktif
    while sesli_mod_aktif:
        s = dinle()
        if s:
            ekrana_yaz("Kaan (Sesli)", s)
            cevap = yapay_zeka_sor(s)
            ekrana_yaz("KaanGemini", cevap)
            konus(cevap)
            time.sleep(1.5)

def sesli_mod_tetikle():
    global sesli_mod_aktif
    if not sesli_mod_aktif:
        sesli_mod_aktif = True
        btn_ses.config(text="🎤 Sesli Mod: AÇIK", bg="#2ecc71")
        threading.Thread(target=sesli_mod_dongusu, daemon=True).start()
    else:
        sesli_mod_aktif = False
        btn_ses.config(text="🎤 Sesli Mod: KAPALI", bg="#e74c3c")

pencere = tk.Tk()
pencere.title("KAAN AI CORE v2.7")
pencere.geometry("550x700")
pencere.configure(bg="#1e1e1e")

chat = scrolledtext.ScrolledText(pencere, bg="#252526", fg="#d4d4d4", font=("Segoe UI", 11), state=tk.DISABLED, wrap=tk.WORD)
chat.pack(padx=15, pady=15, expand=True, fill="both")

alt_panel = tk.Frame(pencere, bg="#1e1e1e")
alt_panel.pack(fill="x", side="bottom", padx=15, pady=10)

entry = tk.Entry(alt_panel, bg="#3c3c3c", fg="white", insertbackground="white", font=("Segoe UI", 12), borderwidth=0)
entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 5))
entry.bind("<Return>", gonder)

btn_gonder = tk.Button(alt_panel, text="GÖNDER", command=gonder, bg="#007acc", fg="white", borderwidth=0, width=10, font=("Segoe UI", 10, "bold"))
btn_gonder.pack(side="right", ipady=8)

btn_ses = tk.Button(pencere, text="🎤 Sesli Mod: KAPALI", command=sesli_mod_tetikle, bg="#e74c3c", fg="white", borderwidth=0, font=("Segoe UI", 10, "bold"))
btn_ses.pack(fill="x", padx=15, pady=(0, 15))

if gecmis:
    ekrana_yaz("SİSTEM", "Hoş geldin Kaan. Bellek hazır.")

pencere.mainloop()
