from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO

app = FastAPI(
    title="API Crawler de Productos",
    description="API para extraer información de productos de tiendas online, incluyendo nombres, precios, URLs e imágenes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Product Crawler API is running", "status": "healthy"}

URL = "https://ilot.co/collections/nueva-coleccion"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    productos = []
    for bloque in soup.select("div.product-inner"):
        a_tag = bloque.select_one("a.cd.chp")
        nombre = a_tag.get_text(strip=True) if a_tag else ""
        enlace = "https://ilot.co" + a_tag.get("href") if a_tag else ""

        precio_tag = bloque.select_one("span.price span.money")
        precio = precio_tag.get_text(strip=True) if precio_tag else "Sin precio"

        img_tag = bloque.select_one("img")
        if img_tag:
            src = img_tag.get("src")
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = "https://ilot.co" + src
        else:
            src = ""

        productos.append({
            "Producto": nombre,
            "URL": enlace,
            "Precio": precio,
            "Imagen": src
        })
    return productos

@app.get("/productos")
async def obtener_productos():
    return {"productos": scrape()}

@app.get("/excel")
async def descargar_excel():
    data = scrape()
    df = pd.DataFrame(data)

    # Generar Excel en memoria
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    # StreamingResponse para descarga directa
    headers = {
        'Content-Disposition': 'attachment; filename="resultados.xlsx"'
    }
    return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    return {"status": "healthy", "message": "API is running"}