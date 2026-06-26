"""Shared dependencies for admin_custom routers.

Mirrors ``is_accessible`` logic from each SQLAdmin ModelView.
"""
from fastapi import Depends, HTTPException, Request, status


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

async def require_admin(request: Request) -> dict:
    """Only users with role 'admin' (matches UserAdmin, PartnerAdmin, PetAdmin,
    ProductAdmin, all Pembayaran*Admin)."""
    role = request.session.get("user_role")
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only admin can access this area.")
    return {"user_role": "admin", "user_id": request.session.get("user_id")}


# ---------------------------------------------------------------------------
# Partner base
# ---------------------------------------------------------------------------

async def require_partner(request: Request) -> dict:
    """Any logged-in partner. Used by JanjiTemuAdmin, DokterPartnerAdmin."""
    role = request.session.get("user_role")
    partner_id = request.session.get("partner_id")
    if role != "partner" or not partner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Partner session required.")
    return {"partner_id": partner_id, "jenis_partner": request.session.get("jenis_partner")}


# ---------------------------------------------------------------------------
# Partner sub-types
# ---------------------------------------------------------------------------

async def require_klinik_partner(request: Request) -> dict:
    """Partner whose jenis_partner is 'klinik' or 'all'."""
    role = request.session.get("user_role")
    partner_id = request.session.get("partner_id")
    jenis = request.session.get("jenis_partner")
    if role != "partner" or not partner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Partner session required.")
    cleaned = str(jenis).strip().lower() if jenis else ""
    if cleaned not in ("klinik", "all"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Access restricted to klinik/all partners.")
    return {"partner_id": partner_id, "jenis_partner": cleaned}


async def require_grooming_partner(request: Request) -> dict:
    """Partner whose jenis_partner is 'grooming' or 'all'."""
    role = request.session.get("user_role")
    partner_id = request.session.get("partner_id")
    jenis = request.session.get("jenis_partner")
    if role != "partner" or not partner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Partner session required.")
    cleaned = str(jenis).strip().lower() if jenis else ""
    if cleaned not in ("grooming", "all"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Access restricted to grooming/all partners.")
    return {"partner_id": partner_id, "jenis_partner": cleaned}
