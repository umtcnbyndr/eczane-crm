"""
Excel Parser Service - ETL for pharmacy data files.

Handles parsing of:
- Grup Bazlı Ürün Satış Raporu (Product Sales)
- Müşteri Ürün Satış Raporu (Customer Sales)
- Müşterilerin Puan ve TL Karşılığı (Customer Points)
"""
import re
import zipfile
import xml.etree.ElementTree as ET
from decimal import Decimal
from datetime import datetime
from django.utils import timezone

from ..models import Customer, Product, SalesTransaction, ExcelUpload


class ExcelParserService:
    """Excel dosyalarını parse eden servis."""

    def __init__(self):
        self.shared_strings = []
        self.ns = ''

    def process_file(self, excel_upload: ExcelUpload) -> dict:
        """Ana işlem fonksiyonu."""
        file_path = excel_upload.file.path
        file_type = excel_upload.file_type

        if file_type == 'CUSTOMER_POINTS':
            return self.parse_customer_points(file_path)
        elif file_type == 'PRODUCT_SALES':
            return self.parse_product_sales(file_path)
        elif file_type == 'CUSTOMER_SALES':
            return self.parse_customer_sales(file_path)
        else:
            raise ValueError(f"Bilinmeyen dosya tipi: {file_type}")

    def _load_xlsx(self, filepath: str) -> tuple:
        """XLSX dosyasını yükle ve shared strings + sheet data döndür."""
        with zipfile.ZipFile(filepath, 'r') as z:
            # Read shared strings
            self.shared_strings = []
            if 'xl/sharedStrings.xml' in z.namelist():
                with z.open('xl/sharedStrings.xml') as ss:
                    tree = ET.parse(ss)
                    root = tree.getroot()
                    self.ns = root.tag.split('}')[0] + '}' if '}' in root.tag else ''
                    for si in root.iter(f'{self.ns}si'):
                        text = ''
                        for t in si.iter(f'{self.ns}t'):
                            if t.text:
                                text += t.text
                        self.shared_strings.append(text)

            # Read sheet
            with z.open('xl/worksheets/sheet1.xml') as sheet:
                tree = ET.parse(sheet)
                root = tree.getroot()
                self.ns = root.tag.split('}')[0] + '}' if '}' in root.tag else ''
                return root

    def _get_cell_value(self, cell) -> str:
        """Hücre değerini al."""
        v = cell.find(f'{self.ns}v')
        t = cell.get('t')

        if v is not None and v.text:
            if t == 's':  # shared string
                idx = int(v.text)
                return self.shared_strings[idx] if idx < len(self.shared_strings) else ''
            return v.text
        return ''

    def _parse_rows(self, root, max_rows=None) -> list:
        """Tüm satırları parse et."""
        rows = []
        row_count = 0

        for row in root.iter(f'{self.ns}row'):
            row_count += 1
            if max_rows and row_count > max_rows:
                break

            cells = {}
            for c in row.iter(f'{self.ns}c'):
                ref = c.get('r')  # e.g., "A1", "B2"
                if ref:
                    # Extract column letter(s)
                    col = ''.join(filter(str.isalpha, ref))
                    cells[col] = self._get_cell_value(c)

            if cells:
                rows.append(cells)

        return rows

    def _clean_phone(self, phone: str) -> str:
        """Telefon numarasını temizle."""
        if not phone:
            return ''
        # Sadece rakamları al
        digits = re.sub(r'\D', '', str(phone))
        # Türkiye formatı
        if len(digits) == 10 and digits.startswith('5'):
            return '0' + digits
        if len(digits) == 11 and digits.startswith('05'):
            return digits
        if len(digits) == 12 and digits.startswith('905'):
            return '0' + digits[2:]
        return digits if len(digits) >= 10 else ''

    def _parse_decimal(self, value: str) -> Decimal:
        """String'i Decimal'e çevir."""
        if not value:
            return Decimal('0')
        try:
            # Türkçe format: 1.234,56 -> 1234.56
            clean = str(value).replace('.', '').replace(',', '.')
            return Decimal(clean)
        except:
            try:
                return Decimal(str(value))
            except:
                return Decimal('0')

    def parse_customer_points(self, filepath: str) -> dict:
        """Müşteri Puan Raporunu parse et."""
        root = self._load_xlsx(filepath)
        rows = self._parse_rows(root)

        created = 0
        updated = 0
        failed = 0

        # Header satırını bul (S.N, Müşteri Adı Soyadı, Cep Telefonları, ...)
        data_started = False
        current_sn = 0

        for row in rows:
            # S.N sütunu varsa veri başlamış demektir
            if 'B' in row and row['B'] == 'S.N':
                data_started = True
                continue

            if not data_started:
                continue

            # Sıra numarası kontrolü (E sütununda)
            sn = row.get('E', '')
            if not sn or not sn.isdigit():
                continue

            sn_int = int(sn)
            if sn_int <= current_sn:
                continue
            current_sn = sn_int

            # Müşteri bilgilerini çıkar
            full_name = row.get('L', '').strip()
            phone = self._clean_phone(row.get('AG', ''))
            phone_secondary = self._clean_phone(row.get('CJ', ''))

            # Puan bilgileri (DH veya DG sütununda olabilir)
            total_points = self._parse_decimal(row.get('DH', '') or row.get('DG', ''))
            points_tl = self._parse_decimal(row.get('DS', ''))

            if not full_name:
                failed += 1
                continue

            # İsmi parçala
            name_parts = full_name.split()
            if len(name_parts) >= 2:
                first_name = ' '.join(name_parts[:-1])
                last_name = name_parts[-1]
            else:
                first_name = full_name
                last_name = ''

            # Müşteri kodu oluştur (telefon veya sıra numarası)
            customer_code = phone if phone else f"CUST{sn_int:06d}"

            try:
                customer, is_created = Customer.objects.update_or_create(
                    customer_code=customer_code,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'phone': phone,
                        'phone_secondary': phone_secondary,
                        'total_points': total_points,
                        'points_tl_value': points_tl,
                    }
                )
                if is_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                failed += 1
                continue

        return {
            'rows_processed': created + updated,
            'rows_failed': failed,
            'created': created,
            'updated': updated
        }

    def parse_product_sales(self, filepath: str) -> dict:
        """Ürün Satış Raporunu parse et."""
        root = self._load_xlsx(filepath)
        rows = self._parse_rows(root)

        created = 0
        updated = 0
        failed = 0

        # Veri satırlarını işle (ilk 2 satır header)
        for row in rows[2:]:
            sn = row.get('A', '')
            if not sn or not sn.isdigit():
                continue

            barcode = row.get('B', '').strip()
            product_code = row.get('C', '').strip()
            name = row.get('D', '').strip()
            kdv = row.get('E', '10')

            if not barcode or not name:
                failed += 1
                continue

            # Alış/Satış bilgileri
            purchase_qty = int(float(row.get('G', '0') or '0'))
            sale_qty = int(float(row.get('K', '0') or '0'))
            unit_price = self._parse_decimal(row.get('J', '0'))

            # Stok = Alış - Satış (basit hesaplama)
            stock = purchase_qty - sale_qty

            try:
                kdv_rate = int(float(kdv)) if kdv else 10
            except:
                kdv_rate = 10

            # Kategori tahmini (ürün adından)
            category = self._guess_category(name)

            try:
                product, is_created = Product.objects.update_or_create(
                    barcode=barcode,
                    defaults={
                        'product_code': product_code,
                        'name': name,
                        'kdv_rate': kdv_rate,
                        'stock_quantity': max(0, stock),
                        'unit_price': unit_price,
                        'category': category,
                    }
                )
                if is_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                failed += 1
                continue

        return {
            'rows_processed': created + updated,
            'rows_failed': failed,
            'created': created,
            'updated': updated
        }

    def _guess_category(self, name: str) -> str:
        """Ürün adından kategori tahmin et."""
        name_lower = name.lower()

        dermo_keywords = ['krem', 'losyon', 'serum', 'şampuan', 'jel', 'spf', 'güneş',
                          'nemlendirici', 'cilt', 'saç', 'yüz', 'vücut', 'kozmetik']
        vitamin_keywords = ['vitamin', 'mineral', 'takviye', 'omega', 'probiyotik',
                            'multivitamin', 'c vitamini', 'd vitamini']
        mama_keywords = ['mama', 'bebek', 'aptamil', 'bebelac', 'hero baby']
        otc_keywords = ['ağrı kesici', 'parol', 'aspirin', 'gripin', 'majezik']

        for kw in dermo_keywords:
            if kw in name_lower:
                return 'DERMO'

        for kw in vitamin_keywords:
            if kw in name_lower:
                return 'VITAMIN'

        for kw in mama_keywords:
            if kw in name_lower:
                return 'MAMA'

        for kw in otc_keywords:
            if kw in name_lower:
                return 'OTC'

        # Default: İlaç
        return 'ILAC'

    def parse_customer_sales(self, filepath: str) -> dict:
        """Müşteri Ürün Satış Raporunu parse et."""
        root = self._load_xlsx(filepath)
        rows = self._parse_rows(root)

        processed = 0
        failed = 0

        # Bu rapor daha karmaşık bir yapıda, gruplandırılmış veri içeriyor
        # Şimdilik basit bir işleme yapacağız

        current_customer = None

        for row in rows:
            # Müşteri satırını bul
            customer_info = row.get('F', '')
            if 'Müsteri Kodu/Adı' in customer_info or 'Müşteri Kodu' in customer_info:
                # Müşteri bilgisini parse et
                # Format: "Müsteri Kodu/Adı : 9990026886 ABDULLAH DİNÇER -  -"
                parts = customer_info.split(':')
                if len(parts) >= 2:
                    customer_data = parts[1].strip()
                    # İlk kelime müşteri kodu, geri kalanı isim
                    customer_parts = customer_data.split()
                    if customer_parts:
                        customer_code = customer_parts[0]
                        name_parts = [p for p in customer_parts[1:] if p != '-']
                        if name_parts:
                            try:
                                current_customer = Customer.objects.filter(
                                    customer_code=customer_code
                                ).first()
                                if not current_customer:
                                    # Yeni müşteri oluştur
                                    full_name = ' '.join(name_parts)
                                    if len(name_parts) >= 2:
                                        first_name = ' '.join(name_parts[:-1])
                                        last_name = name_parts[-1]
                                    else:
                                        first_name = full_name
                                        last_name = ''

                                    current_customer = Customer.objects.create(
                                        customer_code=customer_code,
                                        first_name=first_name,
                                        last_name=last_name
                                    )
                                processed += 1
                            except Exception:
                                failed += 1
                                current_customer = None

        return {
            'rows_processed': processed,
            'rows_failed': failed,
        }
