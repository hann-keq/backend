from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import order_repository as order
from app.schemas.order_schema import schema
from app.exceptions import system_exceptions,user_exceptions

async def create_order(db: AsyncSession, order_data: schema.OrderCreate,user_id: int):
    total = 0.0
    item_details = []

    for item in order_data.items:
        produk = await order.get_ordered_produk_by_id(db, item.id_produk)
        if not produk:
            raise user_exceptions.handle_produk_not_found(f"Produk dengan ID {item.id_produk} tidak ditemukan")
        if produk.stok < item.quantity:
            raise user_exceptions.handle_insufficient_stock(f"Stok untuk produk {produk.nama_produk} tidak mencukupi")
        subtotal = produk.harga * item.quantity
        total += subtotal
        item_details.append((produk, item.quantity, subtotal))
    ordering = await order.create_order_produk(db, {
        "id_user": user_id,
        "total": total,
        "status_order" : "Menunggu"
    })

    for detail in item_details:
        detail['id_order_produk'] = ordering.id_order_produk
        await order.create_order_detail(db, detail)
        await order.kurangi_stok_produk(db, detail['id_produk'], detail['quantity'])
    
    return ordering

async def get_all_order_by_id(db: AsyncSession, user_id: int):
    order_data = await order.get_all_ordered_produk_by_user(db, user_id)
    if not order_data:
        raise user_exceptions.handle_order_not_found(f"Order dengan ID {user_id} tidak ditemukan")
    return order_data

async def get_specific_user_order_by_id(db: AsyncSession, order_id: int):
    order_data = await order.get_ordered_produk_by_id(db, order_id)
    if not order_data:
        raise user_exceptions.handle_order_not_found(f"Order dengan ID {order_id} tidak ditemukan")
    return order_data

async def get_detail_order_by_order_id(db: AsyncSession, id_user: int):
    detail_orders = await order.get_all_ordered_produk_by_user(db, id_user)
    if not detail_orders:
        raise user_exceptions.handle_order_not_found(f"Detail Order untuk User ID {id_user} tidak ditemukan")
    return detail_orders

async def change_status_order(db: AsyncSession, order_id: int, status: str):
    try:
        updated_order = await order.update_status_order(db, order_id, status)
        if not updated_order:
            raise user_exceptions.handle_order_not_found(f"Order dengan ID {order_id} tidak ditemukan")
        return updated_order
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))
    
async def delete_order(db: AsyncSession, order_id: int):
    try:
        deleted_order = await order.delete_order(db, order_id)
        if not deleted_order:
            raise user_exceptions.handle_order_not_found(f"Order dengan ID {order_id} tidak ditemukan")
        return deleted_order
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))
