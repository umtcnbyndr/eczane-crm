# SmartPharmacy CRM

Eczane yönetimi için analitik ve müşteri ilişkileri yönetim sistemi.

## Özellikler

- **Müşteri Yönetimi**: VIP, Dermo VIP, Standart ve Kayıp müşteri segmentasyonu
- **Görev Yönetimi**: Otomatik hatırlatma görevleri, kayıp önleme, VIP takip
- **Gamification**: Personel puan sistemi ve liderlik tablosu
- **Excel Import**: Eczane yazılımından Excel raporları yükleme
- **Replenishment**: Ürün bitiş hatırlatma algoritması

## Teknolojiler

### Backend
- Python 3.11
- Django 5.x
- Django REST Framework
- PostgreSQL
- Pandas (Excel işleme)

### Frontend
- React 18
- Tailwind CSS
- React Router

### DevOps
- Docker & Docker Compose
- Coolify uyumlu

## Kurulum

### Docker ile (Önerilen)

```bash
# Repo'yu klonla
git clone https://github.com/your-repo/eczane-crm.git
cd eczane-crm

# Docker Compose ile başlat
docker-compose up -d

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### Manuel Kurulum

#### Backend

```bash
cd backend

# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Veritabanı migrate
python manage.py migrate

# Örnek veri oluştur (opsiyonel)
python manage.py import_sample_data

# Sunucuyu başlat
python manage.py runserver
```

#### Frontend

```bash
cd frontend

# Bağımlılıkları yükle
npm install

# Development sunucusu
npm start
```

## API Endpoints

### Dashboard
- `GET /api/dashboard/` - Dashboard istatistikleri

### Görevler
- `GET /api/tasks/` - Görev listesi
- `GET /api/tasks/today/` - Bugünün görevleri
- `POST /api/tasks/{id}/complete/` - Görevi tamamla

### Müşteriler
- `GET /api/customers/` - Müşteri listesi
- `GET /api/customers/at_risk/` - Risk altındaki müşteriler
- `GET /api/customers/vip/` - VIP müşteriler

### Ürünler
- `GET /api/products/` - Ürün listesi

### Personel
- `GET /api/staff/` - Personel listesi
- `GET /api/staff/leaderboard/` - Liderlik tablosu

### Excel Upload
- `POST /api/upload/` - Excel yükle
- `GET /api/uploads/` - Yükleme geçmişi

### Aksiyonlar
- `POST /api/generate-tasks/` - Otomatik görev oluştur
- `POST /api/update-segments/` - Müşteri segmentlerini güncelle

## Yönetim Komutları

```bash
# Otomatik görevleri oluştur
python manage.py generate_tasks

# Müşteri segmentlerini güncelle
python manage.py update_segments

# Örnek veri oluştur
python manage.py import_sample_data --customers 100 --products 50
```

## Excel Dosya Formatları

### Müşteri Puan Raporu
- Dosya: `Musterilerin_Puan_ve_TL_Karsiligi_*.xlsx`
- İçerik: Müşteri adı, telefon, puan bilgileri

### Ürün Satış Raporu
- Dosya: `Grup_Bazli_Urun_Satis_Raporu_*.xlsx`
- İçerik: Barkod, ürün adı, stok, fiyat bilgileri

### Müşteri Satış Raporu
- Dosya: `Musteri_Urun_Satis_Raporu_*.xlsx`
- İçerik: Müşteri bazlı satış detayları

## Geliştirme

### Proje Yapısı

```
eczane-crm/
├── backend/
│   ├── smartpharmacy/     # Django settings
│   ├── core/              # Ana uygulama
│   │   ├── models.py      # Veritabanı modelleri
│   │   ├── views.py       # API views
│   │   ├── serializers.py # DRF serializers
│   │   └── services/      # İş mantığı
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React bileşenleri
│   │   ├── pages/         # Sayfa bileşenleri
│   │   └── services/      # API servisleri
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Lisans

MIT License
