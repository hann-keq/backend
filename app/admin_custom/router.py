"""Partner-side routes — HTMX-powered grooming package + janji temu + dokter management.

Routes live under /dashboard-admin/partner/* and are protected by partner-scoped
dependencies that mirror SQLAdmin ``is_accessible`` logic.
"""

import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.core.templates import templates
from app.core.config import UPLOAD_ROOT
from app.models.models import (
    Dokter,
    JanjiTemu,
    PaketGrooming,
    DetailPaketGrooming,
)
from app.admin_custom.deps import (
    require_partner,
    require_klinik_partner,
    require_grooming_partner,
)

router = APIRouter(prefix="/dashboard-admin", tags=["admin_custom_partner"])

_T = "admin_custom"


# ======================================================================
#              PAKET GROOMING  (grooming / all partners)
# ======================================================================

@router.get("/paket", response_class=HTMLResponse, dependencies=[Depends(require_grooming_partner)])
async def paket_list(request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = request.session.get("partner_id")
    result = await db.execute(
        select(PaketGrooming)
        .where(PaketGrooming.id_partner == partner_id)
        .order_by(PaketGrooming.nama_paket_grooming)
    )
    pakets = result.scalars().all()
    return templates.TemplateResponse(request, 
        f"{_T}/manage.html", {"request": request, "pakets": pakets, "partner_id": partner_id},
    )


@router.get("/paket/create", response_class=HTMLResponse, dependencies=[Depends(require_grooming_partner)])
async def paket_create_form(request: Request):
    return templates.TemplateResponse(request, 
        f"{_T}/manage.html", {"request": request, "pakets": [], "jam_tersedia": [""], "is_edit": False},
    )


@router.post("/paket/action/add-jam", response_class=HTMLResponse, dependencies=[Depends(require_grooming_partner)])
async def add_jam(request: Request):
    form = await request.form()
    jam_list = form.getlist("jam_tersedia[]")
    cleaned = [j.strip() for j in jam_list if j.strip()]
    cleaned.append("")
    return templates.TemplateResponse(request, 
        f"{_T}/_form_jam.html", {"request": request, "jam_tersedia": cleaned},
    )


@router.post("/paket/action/remove-jam/{index}", response_class=HTMLResponse, dependencies=[Depends(require_grooming_partner)])
async def remove_jam(index: int, request: Request):
    form = await request.form()
    jam_list = form.getlist("jam_tersedia[]")
    if 0 <= index < len(jam_list):
        del jam_list[index]
    cleaned = [j.strip() for j in jam_list if j.strip()]
    if not cleaned:
        cleaned = [""]
    return templates.TemplateResponse(request, 
        f"{_T}/_form_jam.html", {"request": request, "jam_tersedia": cleaned},
    )


@router.post("/paket/create", dependencies=[Depends(require_grooming_partner)])
async def paket_create(request: Request, db: AsyncSession = Depends(get_db)):
    form = await request.form()
    partner_id = request.session.get("partner_id")
    nama = (form.get("nama_paket") or "").strip()
    harga_raw = (form.get("harga") or "0").strip()
    jam_list = form.getlist("jam_tersedia[]")

    errors: list[str] = []
    if not nama: errors.append("Nama paket wajib diisi.")
    try:
        harga = float(harga_raw)
        if harga <= 0: errors.append("Harga harus > 0.")
    except ValueError:
        errors.append("Harga harus angka."); harga = 0

    jam_bersih = sorted({j.strip() for j in jam_list if j.strip()})

    if errors:
        return templates.TemplateResponse(request, 
            f"{_T}/manage.html", {"request": request, "pakets": [], "jam_tersedia": jam_list or [""],
             "form_errors": errors, "old_nama": nama, "old_harga": harga_raw, "is_edit": False},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    p = PaketGrooming(
        id_partner=partner_id, nama_paket_grooming=nama,
        harga=harga, jam_tersedia=jam_bersih if jam_bersih else None,
    )
    db.add(p)
    await db.commit()
    return RedirectResponse(url="/dashboard-admin/paket", status_code=303)


@router.post("/paket/delete/{paket_id}", dependencies=[Depends(require_grooming_partner)])
async def paket_delete(paket_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = request.session.get("partner_id")
    result = await db.execute(
        select(PaketGrooming).where(
            PaketGrooming.id_paket_grooming == paket_id,
            PaketGrooming.id_partner == partner_id,
        )
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Paket tidak ditemukan.")
    await db.delete(p)
    await db.commit()
    return RedirectResponse(url="/dashboard-admin/paket", status_code=303)


# ======================================================================
#              DETAIL PAKET GROOMING  (grooming / all partners)
# ======================================================================

@router.get("/detail-paket", response_class=HTMLResponse, dependencies=[Depends(require_grooming_partner)])
async def detail_paket_list(request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = request.session.get("partner_id")
    result = await db.execute(
        select(DetailPaketGrooming)
        .join(DetailPaketGrooming.paket)
        .options(joinedload(DetailPaketGrooming.paket))
        .where(PaketGrooming.id_partner == partner_id)
        .order_by(DetailPaketGrooming.id_detail_paket.desc())
    )
    details = result.scalars().all()

    # Fetch partner's packages for the dropdown
    pkg_result = await db.execute(
        select(PaketGrooming).where(PaketGrooming.id_partner == partner_id)
    )
    packages = pkg_result.scalars().all()

    return templates.TemplateResponse(request, 
        f"{_T}/detail_paket_list.html", {"request": request, "details": details, "packages": packages},
    )


@router.post("/detail-paket/create", dependencies=[Depends(require_grooming_partner)])
async def detail_paket_create(request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = request.session.get("partner_id")
    form = await request.form()
    pkg_id = int(form.get("paket_id", 0))
    fitur = str(form.get("fitur", "")).strip()

    # Verify package belongs to this partner
    pkg = await db.get(PaketGrooming, pkg_id)
    if not pkg or pkg.id_partner != partner_id:
        return RedirectResponse(url="/dashboard-admin/detail-paket", status_code=303)

    detail = DetailPaketGrooming(id_paket_grooming=pkg_id, fitur=fitur)
    db.add(detail)
    await db.commit()
    return RedirectResponse(url="/dashboard-admin/detail-paket", status_code=303)


@router.post("/detail-paket/delete/{detail_id}", dependencies=[Depends(require_grooming_partner)])
async def detail_paket_delete(detail_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = request.session.get("partner_id")
    result = await db.execute(
        select(DetailPaketGrooming)
        .join(DetailPaketGrooming.paket)
        .options(joinedload(DetailPaketGrooming.paket))
        .where(
            DetailPaketGrooming.id_detail_paket == detail_id,
            PaketGrooming.id_partner == partner_id,
        )
    )
    detail = result.scalar_one_or_none()
    if detail:
        await db.delete(detail)
        await db.commit()
    return RedirectResponse(url="/dashboard-admin/detail-paket", status_code=303)


# ======================================================================
#              DOKTER  (klinik / all partners)
# ======================================================================

@router.get("/dokter", response_class=HTMLResponse, dependencies=[Depends(require_klinik_partner)])
async def dokter_list(request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = request.session.get("partner_id")
    result = await db.execute(
        select(Dokter)
        .options(joinedload(Dokter.partner))
        .where(Dokter.id_partner == partner_id)
        .order_by(Dokter.nama_dokter)
    )
    dokters = result.scalars().all()
    return templates.TemplateResponse(request, 
        f"{_T}/dokter_list.html", {"request": request, "dokters": dokters},
    )


@router.get("/dokter/create", response_class=HTMLResponse, dependencies=[Depends(require_klinik_partner)])
async def dokter_create_form(request: Request):
    return templates.TemplateResponse(request, 
        f"{_T}/dokter_form.html", {"request": request, "is_edit": False, "dokter_data": {}},
    )


@router.post("/dokter/create", dependencies=[Depends(require_klinik_partner)])
async def dokter_create(request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = request.session.get("partner_id")
    form = await request.form()
    nama = str(form.get("nama_dokter", "")).strip()
    spesialis = str(form.get("spesialis", "")).strip()
    foto_file = form.get("foto")

    errors: list[str] = []
    if not nama: errors.append("Nama dokter wajib diisi.")
    if not spesialis: errors.append("Spesialis wajib diisi.")

    if errors:
        return templates.TemplateResponse(request, 
            f"{_T}/dokter_form.html", {"request": request, "is_edit": False, "dokter_data": {},
             "form_errors": errors, "old_nama": nama, "old_spesialis": spesialis},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    foto_path = None
    if foto_file and hasattr(foto_file, 'filename') and foto_file.filename:
        upload_dir = os.path.join(UPLOAD_ROOT, "dokter")
        os.makedirs(upload_dir, exist_ok=True)
        clean = nama.replace(" ", "_")
        filename = f"{clean}_{foto_file.filename}"
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as buf:
            buf.write(await foto_file.read())
        foto_path = f"/static/uploads/dokter/{filename}"

    d = Dokter(
        id_partner=partner_id, nama_dokter=nama, spesialis=spesialis, foto=foto_path,
    )
    db.add(d)
    await db.commit()
    return RedirectResponse(url="/dashboard-admin/dokter", status_code=303)


@router.post("/dokter/delete/{dokter_id}", dependencies=[Depends(require_klinik_partner)])
async def dokter_delete(dokter_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = request.session.get("partner_id")
    result = await db.execute(
        select(Dokter).where(
            Dokter.id_dokter == dokter_id, Dokter.id_partner == partner_id,
        )
    )
    d = result.scalar_one_or_none()
    if d:
        await db.delete(d)
        await db.commit()
    return RedirectResponse(url="/dashboard-admin/dokter", status_code=303)


# ======================================================================
#              JANJI TEMU  (klinik / all partners)
# ======================================================================

@router.get("/janji-temu", response_class=HTMLResponse, dependencies=[Depends(require_partner)])
async def janji_temu_list(request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = request.session.get("partner_id")
    result = await db.execute(
        select(JanjiTemu)
        .join(JanjiTemu.Dokter)
        .options(
            joinedload(JanjiTemu.Dokter).joinedload(Dokter.partner)
        )
        .where(Dokter.id_partner == partner_id)
        .order_by(JanjiTemu.tanggal_janji.desc(), JanjiTemu.jam_janji.desc())
    )
    janjis = result.scalars().all()
    return templates.TemplateResponse(request, 
        f"{_T}/janji_temu_list.html", {"request": request, "janjis": janjis},
    )
