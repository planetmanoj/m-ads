from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from database import SessionLocal, Ad

app = FastAPI(title="Ad Delivery API")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/serve-ad", response_class=HTMLResponse)
def serve_ad(db: Session = Depends(get_db)):
    """Fetches a random active ad, logs an impression, and returns an HTML banner."""
    # Pick a random active ad
    ad = db.query(Ad).filter(Ad.active == True).order_by(func.random()).first()
    
    if not ad:
        return HTMLResponse(content="<div>No ads available</div>", status_code=404)
    
    # 1. Track the Impression
    ad.impressions += 1
    db.commit()
    db.refresh(ad)
    
    # 2. Build the tracking click URL
    click_url = f"http://localhost:8000/click/{ad.id}" 
    
    # 3. Generate the HTML for the Iframe to display
    html_content = f"""
    <html>
        <body style="margin:0; padding:0; display:flex; justify-content:center; align-items:center; height:100%; font-family:Arial, sans-serif; background-color:#f4f4f4;">
            <a href="{click_url}" target="_blank" style="text-decoration:none; color:black; width:100%; height:100%; display:flex; justify-content:center; align-items:center; border: 1px solid #ccc;">
                <div>
                    <strong>{ad.name}</strong><br>
                    <span style="font-size:12px; color:#666;">Ad by {ad.advertiser}</span>
                </div>
            </a>
        </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/click/{ad_id}")
def register_click(ad_id: int, db: Session = Depends(get_db)):
    """Logs a click and redirects the user to the advertiser's URL."""
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    # Log click
    ad.clicks += 1
    db.commit()
    
    # Redirect to the actual destination
    return RedirectResponse(url=ad.url)
