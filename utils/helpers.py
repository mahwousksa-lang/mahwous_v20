"""
مهووس v20 — دوال مساعدة
"""
import pandas as pd
import io
import re
from datetime import datetime
from config import PRODUCT_COLUMNS, PRICE_COLUMNS, ID_COLUMNS, BRAND_COLUMNS


def read_uploaded_file(uploaded_file):
    """قراءة ملف مرفوع (Excel/CSV) وإرجاع DataFrame"""
    try:
        name = uploaded_file.name.lower()
        if name.endswith('.csv'):
            for encoding in ['utf-8', 'utf-8-sig', 'cp1256', 'iso-8859-6', 'latin-1']:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    if len(df.columns) > 1:
                        return df
                except Exception:
                    continue
        elif name.endswith(('.xlsx', '.xls')):
            uploaded_file.seek(0)
            df = pd.read_excel(uploaded_file)
            return df
        elif name.endswith('.tsv'):
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep='\t')
            return df
    except Exception as e:
        return None
    return None


def find_column(df, candidates):
    """البحث عن عمود من قائمة مرشحين"""
    for col in candidates:
        if col in df.columns:
            return col
        # بحث جزئي
        for df_col in df.columns:
            if col.lower() in str(df_col).lower():
                return df_col
    return None


def extract_products(df, is_my_file=False):
    """
    استخراج المنتجات من DataFrame
    يرجع: [{name, price, product_no, brand}, ...]
    """
    product_col = find_column(df, PRODUCT_COLUMNS)
    price_col = find_column(df, PRICE_COLUMNS)

    if not product_col:
        # محاولة أخيرة: أول عمود نصي
        for col in df.columns:
            if df[col].dtype == 'object':
                product_col = col
                break

    if not product_col:
        return []

    id_col = find_column(df, ID_COLUMNS) if is_my_file else None
    brand_col = find_column(df, BRAND_COLUMNS)

    products = []
    for _, row in df.iterrows():
        name = str(row.get(product_col, "")).strip()
        if not name or name == 'nan':
            continue

        price = 0
        if price_col:
            try:
                p = str(row.get(price_col, "0"))
                p = re.sub(r'[^\d.]', '', p)
                price = float(p) if p else 0
            except (ValueError, TypeError):
                price = 0

        product = {"name": name, "price": price}

        if id_col:
            product["product_no"] = str(row.get(id_col, "")).strip()

        if brand_col:
            product["brand"] = str(row.get(brand_col, "")).strip()

        products.append(product)

    return products


def generate_session_id():
    """إنشاء معرف جلسة فريد"""
    return datetime.now().strftime("S%Y%m%d_%H%M%S")


def format_price(price):
    """تنسيق السعر"""
    if price is None:
        return "—"
    try:
        p = float(price)
        if p == int(p):
            return f"{int(p)}"
        return f"{p:.2f}"
    except (ValueError, TypeError):
        return str(price)


def format_diff(diff, diff_pct=None):
    """تنسيق الفرق"""
    if diff is None:
        return ""
    sign = "+" if diff > 0 else ""
    text = f"{sign}{format_price(diff)}"
    if diff_pct is not None:
        text += f" ({sign}{diff_pct:.1f}%)"
    return text


def products_to_dataframe(products, category=""):
    """تحويل قائمة منتجات إلى DataFrame للتصدير"""
    if not products:
        return pd.DataFrame()

    rows = []
    for p in products:
        row = {}
        if category in ("higher", "lower", "equal", "review"):
            row["رقم المنتج"] = p.get("product_no", "")
            row["منتجك"] = p.get("my_name", "")
            row["سعرك"] = p.get("my_price", "")
            row["منتج المنافس"] = p.get("comp_name", "")
            row["سعر المنافس"] = p.get("comp_price", "")
            row["الفرق"] = p.get("diff", "")
            row["الفرق %"] = p.get("diff_pct", "")
            row["الثقة %"] = p.get("confidence", "")
            row["المنافس"] = p.get("competitor", "")
        elif category == "missing":
            row["المنتج"] = p.get("comp_name", "")
            row["السعر"] = p.get("comp_price", "")
            row["الماركة"] = p.get("brand", "")
            row["المنافس"] = p.get("competitor", "")
            row["أفضل تشابه %"] = p.get("best_score", "")
        elif category == "price_changes":
            row["المنتج"] = p.get("comp_name", "")
            row["السعر القديم"] = p.get("old_price", "")
            row["السعر الجديد"] = p.get("new_price", "")
            row["التغيير"] = p.get("change", "")
            row["المنافس"] = p.get("competitor", "")
        else:
            row = p
        rows.append(row)

    return pd.DataFrame(rows)


def to_excel_bytes(df):
    """تحويل DataFrame إلى bytes Excel"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="البيانات")
    return output.getvalue()


def to_csv_bytes(df):
    """تحويل DataFrame إلى bytes CSV"""
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
