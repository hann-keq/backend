"""Single Jinja2Templates instance — imported by every router and main.py."""
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

def rupiah_format(value):
    try:
        # Memformat angka dengan pemisah koma: 1,000,000
        formatted = f"{int(value):,.0f}".replace(",", ".")
        # Mengubah koma menjadi titik untuk format Indonesia: 1.000.000
        return formatted
    except (ValueError, TypeError):
        return value

templates.env.filters['rupiah'] = rupiah_format