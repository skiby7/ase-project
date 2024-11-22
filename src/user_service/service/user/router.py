from fastapi import APIRouter, HTTPException, Body, Header

from .schemas import User


router = APIRouter(
    prefix="/user",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

@router.get("/userinfo")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

@router.put('/profile/{uid_account}')
def update_user_profile(user_profile: User) -> User:
    return user_profile