
from typing import Optional


from sqlalchemy import Column, Float, Integer, String, ForeignKey, MetaData,Enum,Date,DateTime,Time
from sqlalchemy.orm import DeclarativeBase,mapped_column,Mapped, relationship
from datetime import datetime,time,date
import pytz
from enum import Enum as pyEnum

class Base(DeclarativeBase):
    pass
class RoleUser(pyEnum):
    USER = 'User'
    ADMIN = 'Admin'
    PARTNER = 'Partner'
class JenisHewan(pyEnum):
    KUCING = 'Kucing'
    ANJING = 'Anjing'

class GenderHewan(pyEnum):
    JANTAN = 'Jantan'
    BETINA = 'Betina'

class JenisPartner(pyEnum):
    GROOMING = 'Grooming'
    KLINIK = 'Klinik'
    ALL = 'All'

class StatusBooking(pyEnum):
    MENUNGGU = 'Menunggu'
    SELESAI = 'Selesai'
    DIBATALKAN = 'Dibatalkan'

class OrderStatus(pyEnum):
    MENUNGGU = 'Menunggu'
    DIPROSES = 'Diproses'
    SELESAI = 'Selesai'
    DIBATALKAN = 'Dibatalkan'

class TipeMembership(pyEnum):
    BASIC = 'Basic'
    PREMIUM = 'Premium'
    VIP = 'VIP'

class MetodePembayaran(pyEnum):
    QRIS = 'QRIS'
    GOPAY = 'GoPay'
    TRANSFER_BANK = 'Transfer Bank'

class StatusPembayaran(pyEnum):
    MENUNGGU = 'Menunggu'
    DIBAYAR = 'Dibayar'
    DIBATALKAN = 'Dibatalkan'
    
class User(Base):
    __tablename__ = 'users'
    id_user : Mapped[int] = mapped_column(Integer,primary_key=True)
    nama : Mapped[str] = mapped_column(String(255),nullable=False)
    email : Mapped[str] = mapped_column(String(255),nullable=False,unique=True)
    no_telepon : Mapped[str] = mapped_column(String(20),nullable=False)
    password : Mapped[str] = mapped_column(String(255),nullable=False)
    foto : Mapped[str] = mapped_column(String(255),nullable=True)
    role : Mapped[RoleUser] = mapped_column(Enum(RoleUser),nullable=False,default=RoleUser.USER.value)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

# class Admin(Base):
#     __tablename__ = 'admins'
#     id_admin : Mapped[int] = mapped_column(Integer,primary_key=True)
#     nama : Mapped[str] = mapped_column(String(255),nullable=False)
#     email : Mapped[str] = mapped_column(String(255),nullable=False,unique=True)
#     no_telepon : Mapped[str] = mapped_column(String(20),nullable=False)
#     password : Mapped[str] = mapped_column(String(255),nullable=False)
#     foto : Mapped[str] = mapped_column(String(255),nullable=True)
#     created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
#     updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

class Pet(Base):
    __tablename__ = 'pets'
    id_pet : Mapped[int] = mapped_column(Integer,primary_key=True)
    id_user : Mapped[int] = mapped_column(Integer,ForeignKey('users.id_user'),nullable=False)
    nama_hewan : Mapped[str] = mapped_column(String(255),nullable=False)
    jenis_hewan : Mapped[JenisHewan] = mapped_column(Enum(JenisHewan),nullable=False,default=JenisHewan.KUCING.value)
    umur : Mapped[int] = mapped_column(Integer,nullable=False)
    gender_hewan : Mapped[GenderHewan] = mapped_column(Enum(GenderHewan),nullable=False,default=GenderHewan.JANTAN.value)
    berat : Mapped[float] = mapped_column(Float,nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

class Partner(Base):
    __tablename__ = 'partners'
    id_partner : Mapped[int] = mapped_column(Integer,primary_key=True)
    email : Mapped[str] = mapped_column(String(255),nullable=True,unique=True)
    password : Mapped[str] = mapped_column(String(255),nullable=False)
    nama_partner : Mapped[str] = mapped_column(String(255),nullable=False)
    jenis_partner : Mapped[JenisPartner] = mapped_column(Enum(JenisPartner),nullable=False,default=JenisPartner.ALL.value)
    alamat : Mapped[str] = mapped_column(String(255),nullable=False)
    no_telepon : Mapped[str] = mapped_column(String(20),nullable=False)
    foto : Mapped[str] = mapped_column(String(255),nullable=True)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    def __str__(self):
        return self.nama_partner
class Dokter(Base):
    __tablename__ = 'dokter'
    id_dokter : Mapped[int] = mapped_column(Integer,primary_key=True)
    id_partner : Mapped[int] = mapped_column(Integer,ForeignKey('partners.id_partner'),nullable=False)
    nama_dokter : Mapped[str] = mapped_column(String(255),nullable=False)
    spesialis : Mapped[str] = mapped_column(String(255),nullable=False)
    foto : Mapped[str] = mapped_column(String(255),nullable=True)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    partner: Mapped["Partner"] = relationship("Partner")
class PaketGrooming(Base):
    __tablename__ = 'paket_grooming'
    id_paket_grooming : Mapped[int] = mapped_column(Integer,primary_key=True)
    id_partner : Mapped[int] = mapped_column(Integer,ForeignKey('partners.id_partner'),nullable=False)
    nama_paket_grooming : Mapped[str] = mapped_column(String(255),nullable=False)
    # deskripsi : Mapped[str] = mapped_column(String(255),nullable=False)
    harga : Mapped[float] = mapped_column(Float,nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now,onupdate=datetime.now, nullable=True)

class DetailPaketGrooming(Base):
    __tablename__ = 'detail_paket_grooming'
    id_detail_paket : Mapped[int] = mapped_column(Integer,primary_key=True)
    id_paket_grooming : Mapped[int] = mapped_column(Integer,ForeignKey('paket_grooming.id_paket_grooming'),nullable=False)
    fitur : Mapped[str] = mapped_column(String(255),nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now,onupdate=datetime.now, nullable=True)

class BookingGrooming(Base):
    __tablename__ = 'booking_grooming'
    id_booking_grooming : Mapped[int] = mapped_column(Integer,primary_key=True)
    id_user : Mapped[int] = mapped_column(Integer,ForeignKey('users.id_user'),nullable=False)
    id_pet : Mapped[int] = mapped_column(Integer,ForeignKey('pets.id_pet'),nullable=False)
    id_paket_grooming : Mapped[int] = mapped_column(Integer,ForeignKey('paket_grooming.id_paket_grooming'),nullable=False)
    tanggal_booking : Mapped[date] = mapped_column(Date,nullable=False)
    jam_booking : Mapped[time] = mapped_column(Time,nullable=False)
    status_booking : Mapped[StatusBooking] = mapped_column(Enum(StatusBooking),nullable=False,default=StatusBooking.MENUNGGU.value)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now,onupdate=datetime.now, nullable=True)

class JanjiTemu(Base):
    __tablename__ = 'janji_temu'
    id_janji_temu : Mapped[int] = mapped_column(Integer,primary_key=True)
    id_user : Mapped[int] = mapped_column(Integer,ForeignKey('users.id_user'),nullable=False)
    id_pet : Mapped[int] = mapped_column(Integer,ForeignKey('pets.id_pet'),nullable=False)
    id_dokter : Mapped[int] = mapped_column(Integer,ForeignKey('dokter.id_dokter'),nullable=False)
    tanggal_janji : Mapped[date] = mapped_column(Date,nullable=False)
    keluhan : Mapped[str] = mapped_column(String(255),nullable=False)
    jam_janji : Mapped[time] = mapped_column(Time,nullable=False)
    status_janji : Mapped[StatusBooking] = mapped_column(Enum(StatusBooking),nullable=False,default=StatusBooking.MENUNGGU.value)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now,onupdate=datetime.now, nullable=True)

    Dokter: Mapped["Dokter"] = relationship("Dokter", foreign_keys=[id_dokter])
class Produk(Base):
    __tablename__ = 'produk'
    id_produk : Mapped[int] = mapped_column(Integer,primary_key=True)
    nama_produk : Mapped[str] = mapped_column(String(255),nullable=False)
    # deskripsi : Mapped[str] = mapped_column(String(255),nullable=False)
    harga : Mapped[float] = mapped_column(Float,nullable=False)
    stok : Mapped[int] = mapped_column(Integer,nullable=False)
    gambar : Mapped[str] = mapped_column(String(255),nullable=True)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now,onupdate=datetime.now, nullable=True)

class OrderProduk(Base):
    __tablename__ = 'order_produk'
    id_order_produk : Mapped[int] = mapped_column(Integer,primary_key=True)
    id_user : Mapped[int] = mapped_column(Integer,ForeignKey('users.id_user'),nullable=False)
    total_harga : Mapped[float] = mapped_column(Float,nullable=False)
    status_order : Mapped[OrderStatus] = mapped_column(Enum(OrderStatus),nullable=False,default=OrderStatus.MENUNGGU.value)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now,onupdate=datetime.now, nullable=True)

class DetailOrder(Base):
    __tablename__ = 'detail_order'
    id_detail_order : Mapped[int] = mapped_column(Integer,primary_key=True)
    id_order_produk : Mapped[int] = mapped_column(Integer,ForeignKey('order_produk.id_order_produk'),nullable=False)
    id_produk : Mapped[int] = mapped_column(Integer,ForeignKey('produk.id_produk'),nullable=False)
    jumlah : Mapped[int] = mapped_column(Integer,nullable=False)
    subtotal : Mapped[float] = mapped_column(Float,nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now,onupdate=datetime.now, nullable=True)

class Favorit(Base):
    __tablename__ = 'favorit'
    id_favorit : Mapped[int] = mapped_column(Integer,primary_key=True)
    id_user : Mapped[int] = mapped_column(Integer,ForeignKey('users.id_user'),nullable=False)
    id_produk : Mapped[int] = mapped_column(Integer,ForeignKey('produk.id_produk'),nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now,onupdate=datetime.now, nullable=True)

class Membership(Base):
    __tablename__ = 'membership'
    id_membership : Mapped[int] = mapped_column(Integer,primary_key=True)
    id_user : Mapped[int] = mapped_column(Integer,ForeignKey('users.id_user'),nullable=False)
    tipe_membership : Mapped[TipeMembership] = mapped_column(Enum(TipeMembership),nullable=False,default=TipeMembership.BASIC.value)
    tanggal_berlaku : Mapped[date] = mapped_column(Date,nullable=False)
    tanggal_kedaluarsa : Mapped[date] = mapped_column(Date,nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now,onupdate=datetime.now, nullable=True)

class Alamat(Base):
    __tablename__ = 'alamat'
    id_alamat : Mapped[int] = mapped_column(Integer,primary_key=True)
    id_user : Mapped[int] = mapped_column(Integer,ForeignKey('users.id_user'),nullable=False)
    alamat : Mapped[str] = mapped_column(String(255),nullable=False)
    kota : Mapped[str] = mapped_column(String(100),nullable=False)
    provinsi : Mapped[str] = mapped_column(String(100),nullable=False)
    kode_pos : Mapped[int] = mapped_column(Integer,nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now,onupdate=datetime.now(),nullable=True)

class Pembayaran(Base):
    __tablename__ = 'pembayaran'
    id_pembayaran : Mapped[int] = mapped_column(Integer, primary_key=True)
    id_user : Mapped[int] = mapped_column(Integer, ForeignKey('users.id_user'), nullable=False)
    id_order_produk : Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('order_produk.id_order_produk'), nullable=True)
    id_booking_grooming : Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('booking_grooming.id_booking_grooming'), nullable=True)
    id_janji_temu : Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('janji_temu.id_janji_temu'), nullable=True)
    jumlah_bayar : Mapped[float] = mapped_column(Float, nullable=False)
    metode_pembayaran : Mapped[MetodePembayaran] = mapped_column(Enum(MetodePembayaran), nullable=False, default=MetodePembayaran.QRIS.value)
    status_pembayaran : Mapped[StatusPembayaran] = mapped_column(Enum(StatusPembayaran), nullable=False, default=StatusPembayaran.MENUNGGU.value)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    user: Mapped["User"] = relationship("User", foreign_keys=[id_user])
    
class Cart(Base):
    __tablename__ = 'cart'
    id_cart : Mapped[int] = mapped_column(Integer, primary_key=True)
    id_user : Mapped[int] = mapped_column(Integer, ForeignKey('users.id_user'), nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

class CartItem(Base):
    __tablename__ = 'cart_item'
    id_cart_item : Mapped[int] = mapped_column(Integer, primary_key=True)
    id_cart : Mapped[int] = mapped_column(Integer, ForeignKey('cart.id_cart'), nullable=False)
    id_produk : Mapped[int] = mapped_column(Integer, ForeignKey('produk.id_produk'), nullable=False)
    jumlah : Mapped[int] = mapped_column(Integer, nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

class Receipt(Base):
    __tablename__ = 'receipt'
    id_receipt : Mapped[int] = mapped_column(Integer, primary_key=True)
    id_pembayaran : Mapped[int] = mapped_column(Integer, ForeignKey('pembayaran.id_pembayaran'), nullable=False)
    nomor_receipt : Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    tanggal_bayar : Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)
