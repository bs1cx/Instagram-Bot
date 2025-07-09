import tkinter as tk
from tkinter import ttk, messagebox
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import queue
import time
import webbrowser
from datetime import datetime, timedelta
import pandas as pd
import os

class InstagramHunterPro:
    def __init__(self, root):
        self.root = root
        self.root.title("ANSTASYLE PRO - İnstagram Avcısı")
        self.root.geometry("1400x900")
        self.root.state('zoomed')
        
        # Instagram API client
        self.client = Client()
        self.client.delay_range = [1, 3]
        
        # Filtre değişkenleri
        self.min_followers = tk.StringVar()
        self.max_followers = tk.StringVar()
        self.bio_keywords = tk.StringVar()
        self.location_filter = tk.StringVar()
        
        # Arama parametreleri
        self.stop_event = threading.Event()
        self.result_queue = queue.Queue()
        self.search_active = False
        self.current_results = []
        self.found_user_pks = set()  # Önceki bulunan kullanıcıların PK'larını tutacak
        
        # UI Setup
        self.setup_ui()
        
        # Queue kontrolünü başlat
        self.root.after(100, self.check_queue)

    def setup_ui(self):
        """Profesyonel arayüz oluşturma"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Ana konteyner
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # SOL PANEL
        left_panel = ttk.Frame(main_frame, width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 1. Giriş Bölümü
        self.create_login_section(left_panel)
        
        # 2. Metrikler Paneli
        self.metrics_section = ttk.LabelFrame(left_panel, text="📈 Performans Metrikleri", padding=15)
        self.metrics_section.pack(fill=tk.X, pady=10)
        self.create_metrics_section(self.metrics_section)
        
        # 3. Detaylı Filtre Paneli
        self.create_filter_section(left_panel)
        
        # SAĞ PANEL
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 1. Arama ve Kontroller
        self.create_search_section(right_panel)
        
        # 2. İlerleme çubuğu
        self.progress_frame = ttk.Frame(right_panel)
        self.progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Hazır")
        self.progress_label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X, expand=True)
        
        self.time_label = ttk.Label(self.progress_frame, text="")
        self.time_label.pack(side=tk.RIGHT)
        
        # 3. Sonuçlar Tablosu
        self.create_results_table(right_panel)
        
        # 4. Analiz Paneli
        self.create_analytics_section(right_panel)

    def configure_styles(self):
        """Özel stilleri tanımla"""
        self.style.configure('TFrame', background='#f5f7fa')
        self.style.configure('TLabel', background='#f5f7fa', font=('Segoe UI', 9))
        self.style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#2c3e50')
        self.style.configure('Metric.TLabel', font=('Segoe UI', 18, 'bold'), foreground='#3498db')
        self.style.configure('TButton', padding=5, font=('Segoe UI', 9))
        self.style.configure('Accent.TButton', background='#3498db', foreground='white')
        self.style.map('Accent.TButton', background=[('active', '#2980b9')])
        self.style.configure('Link.TLabel', foreground='blue', font=('Segoe UI', 9, 'underline'))

    def create_login_section(self, parent):
        """Giriş bölümü oluştur"""
        frame = ttk.LabelFrame(parent, text="🔐 Instagram Girişi", padding=15)
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Kullanıcı Adı:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.username_entry = ttk.Entry(frame)
        self.username_entry.grid(row=0, column=1, sticky=tk.EW, pady=3)
        
        ttk.Label(frame, text="Şifre:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.grid(row=1, column=1, sticky=tk.EW, pady=3)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(btn_frame, text="Giriş Yap", command=self.login, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Çıkış Yap", command=self.logout).pack(side=tk.RIGHT, padx=5)
        
        frame.columnconfigure(1, weight=1)

    def create_metrics_section(self, parent):
        """Metrik gösterge paneli"""
        for widget in parent.winfo_children():
            widget.destroy()
            
        self.metrics = {
            "Hesap Büyüme Hızı": "0%",
            "Engagement Oranı": "0%",
            "Toplam Takipçi": "0",
            "Ort. Beğeni": "0"
        }
            
        for metric, value in self.metrics.items():
            row = ttk.Frame(parent)
            row.pack(fill=tk.X, pady=4)
            
            ttk.Label(row, text=metric, width=20).pack(side=tk.LEFT)
            ttk.Label(row, text=value, style='Metric.TLabel').pack(side=tk.RIGHT)
            
        ttk.Button(parent, text="Metrikleri Güncelle", command=self.update_metrics).pack(pady=5)

    def create_filter_section(self, parent):
        """Detaylı filtre paneli"""
        frame = ttk.LabelFrame(parent, text="🔍 Detaylı Filtreleme", padding=15)
        frame.pack(fill=tk.X, pady=10)
        
        # Takipçi Aralığı
        ttk.Label(frame, text="Takipçi Aralığı:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.min_followers_entry = ttk.Entry(frame, textvariable=self.min_followers, width=8)
        self.min_followers_entry.grid(row=0, column=1, padx=2, pady=3)
        ttk.Label(frame, text="-").grid(row=0, column=2)
        self.max_followers_entry = ttk.Entry(frame, textvariable=self.max_followers, width=8)
        self.max_followers_entry.grid(row=0, column=3, padx=2, pady=3)
        
        # Bio Filtresi
        ttk.Label(frame, text="Bio'da Geçenler:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.bio_keywords_entry = ttk.Entry(frame, textvariable=self.bio_keywords)
        self.bio_keywords_entry.grid(row=1, column=1, columnspan=3, sticky=tk.EW, pady=3)
        
        # Lokasyon Filtresi
        ttk.Label(frame, text="Lokasyon:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.location_entry = ttk.Entry(frame, textvariable=self.location_filter)
        self.location_entry.grid(row=2, column=1, columnspan=3, sticky=tk.EW, pady=3)
        
        # Filtrele Butonu
        ttk.Button(frame, text="Filtrele", command=self.apply_filters, 
                  style='Accent.TButton').grid(row=3, column=0, columnspan=4, pady=10)
        
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

    def create_search_section(self, parent):
        """Arama ve kontrol paneli"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Ara:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="Detaylı Arama", command=self.show_advanced_search).pack(side=tk.LEFT, padx=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side=tk.RIGHT)
        
        self.start_btn = ttk.Button(btn_frame, text="Aramayı Başlat", command=self.start_search, style='Accent.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = ttk.Button(btn_frame, text="Durdur", command=self.stop_search, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        self.export_btn = ttk.Button(btn_frame, text="Excel'e Aktar", command=self.export_results)
        self.export_btn.pack(side=tk.LEFT, padx=2)

    def create_results_table(self, parent):
        """Sonuçlar tablosu"""
        frame = ttk.LabelFrame(parent, text="🎯 Bulunan Hesaplar", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ("Kullanıcı", "Takipçi", "Takip", "Post", "Ort. Beğeni", "Lokasyon", "Profil Linki")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=tk.CENTER)
        
        self.tree.column("Profil Linki", width=200)
        
        scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll_y.set)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.open_profile_link)

    def create_analytics_section(self, parent):
        """Analiz paneli"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Top 3 Hesaplar
        top3_frame = ttk.LabelFrame(frame, text="🏆 Top 3 Hesaplar", width=300)
        top3_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.top3_labels = []
        for i in range(3):
            lbl = ttk.Label(top3_frame, text=f"{i+1}. -", font=('Segoe UI', 11))
            lbl.pack(anchor=tk.W, pady=2)
            self.top3_labels.append(lbl)
        
        # Grafik
        graph_frame = ttk.LabelFrame(frame, text="📊 Takipçi Dağılımı")
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=80)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def login(self):
        """Instagram'a giriş yap"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Uyarı", "Kullanıcı adı ve şifre girin!")
            return
            
        try:
            self.client.login(username, password)
            messagebox.showinfo("Başarılı", "Giriş yapıldı!")
            self.update_metrics()
        except LoginRequired as e:
            messagebox.showerror("Hata", "İki faktörlü doğrulama gerekli. Lütfen manuel giriş yapın.")
        except Exception as e:
            messagebox.showerror("Hata", f"Giriş başarısız:\n{str(e)}")

    def logout(self):
        """Çıkış yap"""
        try:
            self.client.logout()
            messagebox.showinfo("Bilgi", "Çıkış yapıldı")
        except Exception as e:
            messagebox.showerror("Hata", f"Çıkış sırasında hata: {str(e)}")

    def show_advanced_search(self):
        """Detaylı arama penceresi"""
        adv_window = tk.Toplevel(self.root)
        adv_window.title("Detaylı Arama")
        adv_window.geometry("500x450")
        
        ttk.Label(adv_window, text="Bio'da Geçen Kelimeler (virgülle ayırın):").pack(pady=5)
        self.adv_bio_keywords = ttk.Entry(adv_window)
        self.adv_bio_keywords.pack(fill=tk.X, padx=10, pady=5)
        
        # Takipçi Filtreleri
        follower_frame = ttk.Frame(adv_window)
        follower_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(follower_frame, text="Takipçi Aralığı:").grid(row=0, column=0, sticky=tk.W)
        
        # Minimum Takipçi
        ttk.Label(follower_frame, text="Min:").grid(row=0, column=1)
        self.adv_min_followers = ttk.Entry(follower_frame, width=10)
        self.adv_min_followers.grid(row=0, column=2, padx=5)
        
        # Maksimum Takipçi
        ttk.Label(follower_frame, text="Max:").grid(row=0, column=3)
        self.adv_max_followers = ttk.Entry(follower_frame, width=10)
        self.adv_max_followers.grid(row=0, column=4, padx=5)
        
        # Lokasyon Filtresi
        ttk.Label(adv_window, text="Lokasyon:").pack(pady=5)
        self.adv_location = ttk.Entry(adv_window)
        self.adv_location.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(adv_window, text="Ara", command=lambda: [self.start_search(True), adv_window.destroy()], 
                 style='Accent.TButton').pack(pady=15)

    def start_search(self, advanced=False):
        """Aramayı başlat"""
        if self.search_active:
            messagebox.showwarning("Uyarı", "Zaten bir arama devam ediyor!")
            return
            
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Uyarı", "Arama kriteri girin!")
            return
            
        # Temizle ve başlat
        self.tree.delete(*self.tree.get_children())
        self.current_results = []
        self.found_user_pks.clear()  # Yeni arama için önceki kullanıcılar sıfırlanır
        self.stop_event.clear()
        self.search_active = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Arama başladı...")
        
        # Filtreleri hazırla
        filters = {}
        if advanced:
            filters['bio_keywords'] = [kw.strip().lower() for kw in self.adv_bio_keywords.get().split(",") if kw.strip()]
            
            # Minimum takipçi
            try:
                min_followers = self.adv_min_followers.get()
                filters['min_followers'] = int(min_followers) if min_followers else None
            except ValueError:
                messagebox.showerror("Hata", "Geçersiz minimum takipçi sayısı!")
                return
            
            # Maksimum takipçi
            try:
                max_followers = self.adv_max_followers.get()
                filters['max_followers'] = int(max_followers) if max_followers else None
            except ValueError:
                messagebox.showerror("Hata", "Geçersiz maksimum takipçi sayısı!")
                return
            
            filters['location'] = self.adv_location.get() if self.adv_location.get() else None
        
        # Thread başlat
        threading.Thread(
            target=self.search_profiles,
            args=(query, filters),
            daemon=True
        ).start()

    def search_profiles(self, query, filters):
        """Profilleri ara (API kullanarak)"""
        try:
            start_time = time.time()
            users = self.client.search_users(query)
            self.result_queue.put({"total": len(users)})
            
            for i, user in enumerate(users):
                if self.stop_event.is_set():
                    break
                
                # Daha önce bulunan kullanıcıyı atla
                if user.pk in self.found_user_pks:
                    continue
                
                try:
                    # Kullanıcı detaylarını al
                    user_info = self.client.user_info(user.pk)
                    
                    # Filtreleme
                    if filters.get('bio_keywords'):
                        bio = (user_info.biography or "").lower()
                        if not any(keyword in bio for keyword in filters['bio_keywords']):
                            continue
                    
                    # Minimum takipçi filtresi
                    if filters.get('min_followers') is not None:
                        if user_info.follower_count < filters['min_followers']:
                            continue
                    
                    # Maksimum takipçi filtresi
                    if filters.get('max_followers') is not None:
                        if user_info.follower_count > filters['max_followers']:
                            continue
                    
                    # Lokasyon filtresi
                    if filters.get('location'):
                        profile_loc = (user_info.city_name or "").lower()
                        if not profile_loc or filters['location'].lower() not in profile_loc:
                            continue
                    
                    # Son 3 postun ortalamasını al
                    medias = self.client.user_medias(user.pk, amount=3)
                    avg_likes = sum(m.like_count for m in medias)/len(medias) if medias else 0
                    
                    # Sonuç hazırla
                    profile_data = {
                        "username": user_info.username,
                        "followers": user_info.follower_count,
                        "following": user_info.following_count,
                        "posts": user_info.media_count,
                        "avg_likes": int(avg_likes),
                        "location": user_info.city_name or "Belirtilmemiş",
                        "profile_url": f"https://instagram.com/{user_info.username}"
                    }
                    
                    self.found_user_pks.add(user.pk)  # Yeni kullanıcı set'e eklendi
                    
                    # Kuyruğa gönder
                    self.result_queue.put(profile_data)
                    self.current_results.append(profile_data)
                    
                    # İlerleme ve zaman güncelle
                    progress = int(((i + 1) / len(users)) * 100)
                    self.result_queue.put({"progress": progress})
                    elapsed = time.time() - start_time
                    remaining = (elapsed / (i + 1)) * (len(users) - (i + 1))
                    self.result_queue.put({"time": remaining})
                    
                    time.sleep(2)
                
                except Exception as e:
                    print(f"Kullanıcı işlenirken hata: {str(e)}")
                    continue
            
            self.result_queue.put({"done": True})
        
        except Exception as e:
            self.result_queue.put({"error": str(e)})

    def check_queue(self):
        """Arama sonuçlarını ve ilerlemeyi UI'ye yansıt"""
        try:
            while True:
                item = self.result_queue.get_nowait()
                if 'total' in item:
                    self.progress_label.config(text=f"Toplam hesap: {item['total']}")
                elif 'progress' in item:
                    self.progress_bar['value'] = item['progress']
                    self.progress_label.config(text=f"İlerleme: %{item['progress']}")
                elif 'time' in item:
                    seconds = int(item['time'])
                    m, s = divmod(seconds, 60)
                    self.time_label.config(text=f"Kalan süre: {m}dk {s}s")
                elif 'done' in item:
                    self.progress_label.config(text="Arama tamamlandı!")
                    self.search_active = False
                    self.start_btn.config(state=tk.NORMAL)
                    self.stop_btn.config(state=tk.DISABLED)
                    self.time_label.config(text="")
                    self.update_results_table()
                    self.update_analytics()
                elif 'error' in item:
                    messagebox.showerror("Hata", item['error'])
                    self.search_active = False
                    self.start_btn.config(state=tk.NORMAL)
                    self.stop_btn.config(state=tk.DISABLED)
                else:
                    # Yeni profil eklendi
                    self.insert_result_row(item)
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_queue)

    def insert_result_row(self, profile_data):
        """Sonuç tablosuna satır ekle"""
        values = (
            profile_data["username"],
            profile_data["followers"],
            profile_data["following"],
            profile_data["posts"],
            profile_data["avg_likes"],
            profile_data["location"],
            profile_data["profile_url"]
        )
        self.tree.insert("", tk.END, values=values)

    def update_results_table(self):
        """Tabloyu güncelle (örneğin filtre sonrası)"""
        self.tree.delete(*self.tree.get_children())
        for profile_data in self.current_results:
            self.insert_result_row(profile_data)

    def stop_search(self):
        """Aramayı durdur"""
        if not self.search_active:
            return
        self.stop_event.set()
        self.progress_label.config(text="Arama durduruluyor...")

    def apply_filters(self):
        """Filtreleri uygula (ana ekrandaki filtreler için)"""
        bio_filter = self.bio_keywords.get().strip().lower()
        min_fol = self.min_followers.get()
        max_fol = self.max_followers.get()
        loc_filter = self.location_filter.get().strip().lower()
        
        filtered = []
        for prof in self.current_results:
            bio_ok = True
            if bio_filter:
                # Burada bio filtresi yok, çünkü current_results'da bio yok
                bio_ok = True
            
            min_ok = True
            max_ok = True
            try:
                if min_fol:
                    min_ok = int(prof['followers']) >= int(min_fol)
                if max_fol:
                    max_ok = int(prof['followers']) <= int(max_fol)
            except Exception:
                min_ok = max_ok = True
            
            loc_ok = True
            if loc_filter:
                loc_ok = loc_filter in prof['location'].lower()
            
            if bio_ok and min_ok and max_ok and loc_ok:
                filtered.append(prof)
        
        self.tree.delete(*self.tree.get_children())
        for profile_data in filtered:
            self.insert_result_row(profile_data)
            
        self.progress_label.config(text=f"Filtre uygulandı. {len(filtered)} hesap gösteriliyor.")

    def update_metrics(self):
        """Metriklerin güncellenmesi (örnek statik)"""
        # Buraya Instagram API'den çekilen gerçek metrikler gelebilir
        self.metrics = {
            "Hesap Büyüme Hızı": "12%",
            "Engagement Oranı": "4.8%",
            "Toplam Takipçi": "25.480",
            "Ort. Beğeni": "3.212"
        }
        self.create_metrics_section(self.metrics_section)

    def update_analytics(self):
        """Basit analizler ve grafik"""
        if not self.current_results:
            return
        
        # Top 3 ortalama beğeniye göre
        top3 = sorted(self.current_results, key=lambda x: x['avg_likes'], reverse=True)[:3]
        for i, prof in enumerate(top3):
            self.top3_labels[i].config(text=f"{i+1}. {prof['username']} - Ortalama Beğeni: {prof['avg_likes']}")
        
        # Takipçi dağılım grafiği
        followers = [p['followers'] for p in self.current_results]
        bins = [0, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
        self.ax.clear()
        self.ax.hist(followers, bins=bins, color='#3498db', edgecolor='black')
        self.ax.set_title("Takipçi Dağılımı")
        self.ax.set_xlabel("Takipçi Sayısı")
        self.ax.set_ylabel("Hesap Sayısı")
        self.fig.tight_layout()
        self.canvas.draw()

    def open_profile_link(self, event):
        """Tablodan profil linkini çift tıklayınca aç"""
        item = self.tree.selection()[0]
        url = self.tree.item(item, "values")[6]
        webbrowser.open(url)

    def export_results(self):
        """Excel'e aktar"""
        if not self.current_results:
            messagebox.showinfo("Bilgi", "Dışa aktarılacak veri yok.")
            return
        
        df = pd.DataFrame(self.current_results)
        filename = f"insta_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        messagebox.showinfo("Başarılı", f"Sonuçlar '{filename}' olarak kaydedildi.")


if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramHunterPro(root)
    root.mainloop()
