"""
Excel Parser Service - ETL for pharmacy data files.

Handles parsing of Tria pharmacy system exports:
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
    """Excel dosyalarını parse eden servis - Tria uyumlu."""

    # Tria uses strict OOXML namespace
    STRICT_NS = 'http://purl.oclc.org/ooxml/spreadsheetml/main'
    STANDARD_NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'

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

    def _load_xlsx(self, filepath: str):
        """XLSX dosyasını yükle ve shared strings + rows döndür."""
        with zipfile.ZipFile(filepath, 'r') as z:
            # Read shared strings
            self.shared_strings = []
            if 'xl/sharedStrings.xml' in z.namelist():
                with z.open('xl/sharedStrings.xml') as ss:
                    content = ss.read().decode('utf-8')
                    root = ET.fromstring(content)

                    # Detect namespace
                    if root.tag.startswith('{'):
                        self.ns = root.tag.split('}')[0] + '}'
                    else:
                        self.ns = ''

                    # Try both strict and standard namespaces
                    for ns_uri in [self.STRICT_NS, self.STANDARD_NS]:
                        ns = {'ns': ns_uri}
                        strings = root.findall('.//ns:t', ns)
                        if strings:
                            self.shared_strings = [s.text or '' for s in strings]
                            break

            # Read sheet
            with z.open('xl/worksheets/sheet1.xml') as sheet:
                content = sheet.read().decode('utf-8')
                root = ET.fromstring(content)

                # Detect namespace from sheet
                if root.tag.startswith('{'):
                    self.ns = root.tag.split('}')[0] + '}'

                return root

    def _get_cell_value(self, cell) -> str:
        """Hücre değerini al."""
        # Try with namespace
        v = cell.find(f'{self.ns}v')
        if v is None:
            # Try without namespace
            v = cell.find('v')

        t = cell.get('t')

        if v is not None and v.text:
            if t == 's':  # shared string
                idx = int(v.text)
                return self.shared_strings[idx] if idx < len(self.shared_strings) else ''
            return v.text
        return ''

    def _col_to_index(self, col: str) -> int:
        """Excel sütun harfini indekse çevir (A=0, B=1, ..., AA=26, AB=27, ...)."""
        result = 0
        for char in col.upper():
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result - 1

    def _parse_rows_to_dict(self, root) -> list:
        """Satırları dict olarak parse et."""
        rows = []

        # Try both namespaces for finding rows
        for ns_uri in [self.STRICT_NS, self.STANDARD_NS, '']:
            if ns_uri:
                ns = {'ns': ns_uri}
                row_elements = root.findall('.//ns:row', ns)
            else:
                row_elements = root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row')

            if row_elements:
                for row in row_elements:
                    row_num = row.get('r', '')
                    cells = {}

                    # Find cells
                    for ns_test in [ns_uri, '']:
                        if ns_test:
                            cell_elements = row.findall('{' + ns_test + '}c')
                        else:
                            cell_elements = list(row)

                        for c in cell_elements:
                            if c.tag.endswith('}c') or c.tag == 'c':
                                ref = c.get('r', '')
                                if ref:
                                    col = ''.join(filter(str.isalpha, ref))
                                    cells[col] = self._get_cell_value(c)

                    if cells:
                        cells['_row'] = row_num
                        rows.append(cells)
                break

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

    def _parse_date(self, value: str) -> datetime:
        """Tarih parse et."""
        if not value:
            return timezone.now()

        # Try different date formats
        formats = ['%d/%m/%Y', '%d.%m.%Y', '%Y-%m-%d', '%d-%m-%Y']
        for fmt in formats:
            try:
                return datetime.strptime(value.strip(), fmt)
            except:
                continue

        return timezone.now()

    def parse_customer_points(self, filepath: str) -> dict:
        """
        Tria Müşteri Puan Raporunu parse et.

        Tria Format (actual structure):
        - Row 7: Headers
        - Row 11+: Each customer data is in a SINGLE row
          - E or D: serial number
          - L: customer name
          - AG: mobile phone
          - CJ: landline
          - DG or DH: total points
          - DS or DT: points TL value
        """
        root = self._load_xlsx(filepath)
        rows = self._parse_rows_to_dict(root)

        created = 0
        updated = 0
        failed = 0
        skipped = 0

        # Find header row first
        header_found = False

        for row in rows:
            # Check for header row (contains S.N)
            row_values = [str(v) for v in row.values() if v and v != row.get('_row')]
            if 'S.N' in row_values or 'Müşteri Adı Soyadı' in ' '.join(row_values):
                header_found = True
                continue

            if not header_found:
                continue

            # Look for serial number in E, D, C, or A column (Tria changes column based on digit count)
            sn = row.get('E', '') or row.get('D', '') or row.get('C', '') or row.get('A', '')
            full_name = row.get('L', '').strip()

            # Skip if no serial number or no name
            if not sn or not full_name:
                continue

            # Parse serial number
            try:
                sn_int = int(float(sn))
            except:
                continue

            # Skip summary rows
            if 'toplam' in full_name.lower() or 'genel' in full_name.lower():
                skipped += 1
                continue

            # Get phone numbers from same row
            phone = self._clean_phone(row.get('AG', ''))
            phone_secondary = self._clean_phone(row.get('CJ', ''))

            # Get points - try multiple columns (DG, DH, DF, DI)
            total_points = Decimal('0')
            for col in ['DG', 'DH', 'DF', 'DI']:
                val = row.get(col, '')
                if val:
                    total_points = self._parse_decimal(val)
                    if total_points > 0:
                        break

            # Get points TL value - try multiple columns (DS, DT, DQ)
            points_tl = Decimal('0')
            for col in ['DS', 'DT', 'DQ']:
                val = row.get(col, '')
                if val:
                    points_tl = self._parse_decimal(val)
                    if points_tl > 0:
                        break

            # Parse name
            name_parts = full_name.split()
            if len(name_parts) >= 2:
                first_name = ' '.join(name_parts[:-1])
                last_name = name_parts[-1]
            else:
                first_name = full_name
                last_name = ''

            # Generate customer code
            customer_code = f"TRIA{sn_int:08d}"

            try:
                # Check if customer exists by phone
                existing = None
                if phone:
                    existing = Customer.objects.filter(phone=phone).first()

                if existing:
                    # Update existing customer
                    existing.total_points = total_points
                    existing.points_tl_value = points_tl
                    if phone_secondary and not existing.phone_secondary:
                        existing.phone_secondary = phone_secondary
                    existing.save()
                    updated += 1
                else:
                    # Create new customer
                    Customer.objects.create(
                        customer_code=customer_code,
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone,
                        phone_secondary=phone_secondary,
                        total_points=total_points,
                        points_tl_value=points_tl,
                    )
                    created += 1
            except Exception as e:
                failed += 1
                continue

        return {
            'rows_processed': created + updated,
            'rows_failed': failed,
            'rows_skipped': skipped,
            'created': created,
            'updated': updated
        }

    def parse_product_sales(self, filepath: str) -> dict:
        """
        Tria Grup Bazlı Ürün Satış Raporunu parse et.
        """
        root = self._load_xlsx(filepath)
        rows = self._parse_rows_to_dict(root)

        created = 0
        updated = 0
        failed = 0

        # Veri satırlarını işle
        for row in rows:
            # Barkod sütununu bul
            barcode = ''
            name = ''

            for col, val in row.items():
                if col == '_row':
                    continue
                # Barkod formatı: 13 haneli sayı veya 868... ile başlayan
                if val and re.match(r'^\d{8,14}$', str(val).strip()):
                    barcode = str(val).strip()
                # Ürün adı genellikle uzun text
                elif val and len(str(val)) > 10 and not val.isdigit():
                    if not name:
                        name = str(val).strip()

            if not barcode:
                continue

            # Kategori tahmini
            category = self._guess_category(name) if name else 'ILAC'

            try:
                product, is_created = Product.objects.update_or_create(
                    barcode=barcode,
                    defaults={
                        'name': name or f'Ürün {barcode}',
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
        if not name:
            return 'ILAC'
        name_lower = name.lower()

        dermo_keywords = ['krem', 'losyon', 'serum', 'şampuan', 'jel', 'spf', 'güneş',
                          'nemlendirici', 'cilt', 'saç', 'yüz', 'vücut', 'kozmetik',
                          'la roche', 'vichy', 'bioderma', 'avene', 'eucerin']
        vitamin_keywords = ['vitamin', 'mineral', 'takviye', 'omega', 'probiyotik',
                            'multivitamin', 'c vitamini', 'd vitamini', 'eff', 'tablet',
                            'kapsül', 'youplus', 'solgar']
        mama_keywords = ['mama', 'bebek', 'aptamil', 'bebelac', 'hero baby', 'hipp']
        otc_keywords = ['ağrı kesici', 'parol', 'aspirin', 'gripin', 'majezik', 'nurofen']

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

        return 'ILAC'

    def parse_customer_sales(self, filepath: str) -> dict:
        """
        Tria Müşteri Ürün Satış Raporunu parse et.

        Tria Format:
        - Mal Grup başlıkları
        - Müşteri Kodu/Adı satırları
        - Ürün satış detayları

        Columns (detected from row 23):
        G: Ürün Kodu, I: Ürün Adı, P: Sat.Tarihi, R: Miktar, V: Net Satış, Z: KDV
        """
        root = self._load_xlsx(filepath)
        rows = self._parse_rows_to_dict(root)

        transactions_created = 0
        products_created = 0
        customers_created = 0
        failed = 0

        current_customer = None
        current_customer_code = None

        # Column mapping
        col_map = {
            'product_code': 'G',
            'product_name': 'I',
            'date': 'P',
            'quantity': 'R',
            'net_sales': 'V',
            'kdv': 'Z',
            'gross_sales': 'AJ'
        }

        import logging
        logger = logging.getLogger(__name__)

        for row in rows:
            row_values = ' '.join([str(v) for k, v in row.items() if k != '_row' and v])
            row_values_lower = row_values.lower()

            # Müşteri satırını bul - hem 's' hem 'ş' karakterini kontrol et
            is_customer_row = (
                'müsteri kodu' in row_values_lower or
                'müşteri kodu' in row_values_lower or
                'musteri kodu' in row_values_lower
            )

            if is_customer_row:
                # Müşteri bilgisini parse et
                for col, val in row.items():
                    if col == '_row':
                        continue
                    val_str = str(val)
                    val_lower = val_str.lower()
                    if 'müsteri kodu' in val_lower or 'müşteri kodu' in val_lower or 'musteri kodu' in val_lower:
                        # Format: "Müsteri Kodu/Adı : 9990026886 ABDULLAH DİNÇER -  -"
                        parts = val_str.split(':')
                        if len(parts) >= 2:
                            customer_data = parts[1].strip()
                            customer_parts = customer_data.split()
                            if customer_parts:
                                customer_code = customer_parts[0]
                                name_parts = [p for p in customer_parts[1:] if p != '-' and p.strip()]

                                if name_parts:
                                    full_name = ' '.join(name_parts)
                                    if len(name_parts) >= 2:
                                        first_name = ' '.join(name_parts[:-1])
                                        last_name = name_parts[-1]
                                    else:
                                        first_name = full_name
                                        last_name = ''

                                    try:
                                        logger.info(f"Looking for customer: first_name='{first_name}', last_name='{last_name}'")

                                        # Try to find customer by name (first + last)
                                        current_customer = Customer.objects.filter(
                                            first_name__iexact=first_name,
                                            last_name__iexact=last_name
                                        ).first()

                                        # If not found, try by full name in first_name field
                                        if not current_customer:
                                            current_customer = Customer.objects.filter(
                                                first_name__iexact=full_name
                                            ).first()

                                        # If not found, try partial match on first name
                                        if not current_customer:
                                            current_customer = Customer.objects.filter(
                                                first_name__icontains=first_name
                                            ).first()

                                        # If still not found, create new customer
                                        if not current_customer:
                                            current_customer = Customer.objects.create(
                                                customer_code=f"TRIA{customer_code}",
                                                first_name=first_name,
                                                last_name=last_name
                                            )
                                            customers_created += 1
                                            logger.info(f"Created new customer: {first_name} {last_name}")
                                        else:
                                            logger.info(f"Found existing customer: {current_customer.first_name} {current_customer.last_name}")

                                        current_customer_code = customer_code
                                    except Exception as e:
                                        logger.error(f"Error finding/creating customer: {e}")
                                        current_customer = None
                        break
                continue

            # Header satırını atla - Türkçe karakter varyasyonları
            if 'ürün kodu' in row_values_lower or 'urun kodu' in row_values_lower:
                # Dinamik olarak sütunları bul
                logger.info(f"Found header row, detecting columns...")
                for col, val in row.items():
                    if col == '_row':
                        continue
                    val_str = str(val).strip().lower()
                    if 'ürün kodu' in val_str or 'urun kodu' in val_str:
                        col_map['product_code'] = col
                        logger.info(f"Product code column: {col}")
                    elif 'ürün adı' in val_str or 'urun adi' in val_str:
                        col_map['product_name'] = col
                        logger.info(f"Product name column: {col}")
                    elif 'tarih' in val_str:
                        col_map['date'] = col
                    elif 'miktar' in val_str:
                        col_map['quantity'] = col
                    elif 'net' in val_str and 'sat' in val_str:
                        col_map['net_sales'] = col
                    elif 'kdv' in val_str:
                        col_map['kdv'] = col
                continue

            # Toplam satırlarını atla
            if 'toplam' in row_values_lower or 'genel' in row_values_lower:
                continue

            # Ürün satış verisi - ürün kodu varsa işle
            product_code = row.get(col_map['product_code'], '').strip()
            if not product_code or not product_code[0].isdigit():
                continue

            product_name = row.get(col_map['product_name'], '').strip()
            sale_date_str = row.get(col_map['date'], '')
            quantity_str = row.get(col_map['quantity'], '1')
            net_sales_str = row.get(col_map['net_sales'], '0')
            kdv_str = row.get(col_map['kdv'], '0')

            if not product_name:
                continue

            # Parse values
            try:
                quantity = int(float(quantity_str)) if quantity_str else 1
            except:
                quantity = 1

            net_sales = self._parse_decimal(net_sales_str)
            kdv = self._parse_decimal(kdv_str)
            sale_date = self._parse_date(sale_date_str)

            # Birim fiyat hesapla
            unit_price = net_sales / quantity if quantity > 0 else net_sales

            # Ürünü oluştur/güncelle
            try:
                product, prod_created = Product.objects.get_or_create(
                    product_code=product_code,
                    defaults={
                        'name': product_name,
                        'barcode': product_code,  # Ürün kodunu barkod olarak kullan
                        'unit_price': unit_price,
                        'category': self._guess_category(product_name),
                    }
                )
                if prod_created:
                    products_created += 1
                    if products_created <= 5:
                        logger.info(f"Created product: {product_code} - {product_name}")

                # Satış kaydı oluştur
                if current_customer:
                    SalesTransaction.objects.create(
                        customer=current_customer,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_amount=net_sales,
                        kdv_amount=kdv,
                        transaction_date=sale_date,
                    )
                    transactions_created += 1

                    # Müşteri puanını güncelle (her 1 TL = 1 puan varsayımı)
                    current_customer.total_points += net_sales
                    current_customer.save()
                else:
                    # Log when product is created but no customer for transaction
                    if products_created <= 5:
                        logger.warning(f"Product created but no current customer for transaction: {product_code}")

            except Exception as e:
                logger.error(f"Error creating product/transaction: {e}")
                failed += 1
                continue

        logger.info(f"Sales parse complete: transactions={transactions_created}, products={products_created}, customers={customers_created}, failed={failed}")

        return {
            'rows_processed': transactions_created + products_created + customers_created,
            'transactions_created': transactions_created,
            'products_created': products_created,
            'customers_created': customers_created,
            'rows_failed': failed,
        }
