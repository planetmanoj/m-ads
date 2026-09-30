from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
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

@app.get("/serve-ad")
def serve_ad(db: Session = Depends(get_db)):
    """Fetches a random active ad, logs an impression, and returns the ad data."""
    # Pick a random active ad
    ad = db.query(Ad).filter(Ad.active == True).order_by(func.random()).first()
    
    if not ad:
        raise HTTPException(status_code=404, detail="No active ads available")
    
    # Log impression
    ad.impressions += 1
    db.commit()
    db.refresh(ad)
    
    # Return ad payload to the publisher
    return {
        "ad_id": ad.id,
        "name": ad.name,
        "advertiser": ad.advertiser,
        "type": ad.type,
        "click_url": f"http://localhost:8000/click/{ad.id}" # Route through our API to track clicks
    }

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
