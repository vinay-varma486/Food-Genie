from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from deps import get_db, get_current_user
from model_user import User
from schema_cart import (
    CartResponse,
    CartItemAddRequest,
    CartItemUpdateRequest,
    CartSaveRequest,
)
from cart_service import (
    build_cart_response,
    add_item_to_cart,
    update_cart_item,
    remove_cart_item,
    clear_user_cart,
    save_user_cart,
)
from pdf_service import generate_food_cart_pdf

router = APIRouter(prefix="/cart", tags=["My Food Cart"])


@router.get(
    "",
    response_model=CartResponse,
    summary="Get authenticated user's persistent Food Cart",
)
def get_my_food_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return build_cart_response(db, current_user)


@router.post(
    "/items",
    response_model=CartResponse,
    summary="Add food item to Food Cart (auto-merges duplicate meal entries)",
)
def add_food_to_cart(
    item_in: CartItemAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_item_to_cart(db, current_user, item_in)


@router.put(
    "/items/{item_id}",
    response_model=CartResponse,
    summary="Update cart item quantity, meal slot, or details",
)
def update_my_cart_item(
    item_id: int,
    item_upd: CartItemUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_cart_item(db, current_user, item_id, item_upd)


@router.delete(
    "/items/{item_id}",
    response_model=CartResponse,
    summary="Remove an item from My Food Cart",
)
def delete_my_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return remove_cart_item(db, current_user, item_id)


@router.delete(
    "",
    response_model=CartResponse,
    summary="Clear all items in My Food Cart",
)
def clear_my_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return clear_user_cart(db, current_user)


@router.post(
    "/save",
    summary="Save Food Cart to user account and optionally snapshot as meal plan",
)
def save_my_cart(
    req: CartSaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return save_user_cart(db, current_user, req)


@router.get(
    "/pdf",
    summary="Download My Food Cart & daily nutrition summary as printable PDF",
)
def download_food_cart_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart_data = build_cart_response(db, current_user)
    pdf_bytes = generate_food_cart_pdf(current_user, cart_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="foodgenie-food-cart.pdf"'
        },
    )

