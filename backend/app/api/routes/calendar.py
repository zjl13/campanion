from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.serializers import serialize_calendar_block
from app.db.session import get_db
from app.models.planning import CalendarBlock
from app.models.user import User
from app.schemas.calendar import CalendarBlockCreateRequest, CalendarBlockResponse


router = APIRouter(prefix="/calendar/blocks", tags=["calendar"])


@router.get("", response_model=list[CalendarBlockResponse])
def list_blocks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CalendarBlockResponse]:
    blocks = db.scalars(
        select(CalendarBlock)
        .where(CalendarBlock.user_id == current_user.id)
        .order_by(CalendarBlock.weekday.asc(), CalendarBlock.start_time.asc())
    ).all()
    return [CalendarBlockResponse.model_validate(serialize_calendar_block(block)) for block in blocks]


@router.post("", response_model=CalendarBlockResponse)
def create_block(
    payload: CalendarBlockCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalendarBlockResponse:
    block = CalendarBlock(
        user_id=current_user.id,
        title=payload.title,
        block_type=payload.type,
        weekday=payload.weekday,
        start_time=payload.start_time,
        end_time=payload.end_time,
        repeat_rule=payload.repeat,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(block)
    db.commit()
    db.refresh(block)
    return CalendarBlockResponse.model_validate(serialize_calendar_block(block))


@router.put("/{block_id}", response_model=CalendarBlockResponse)
def update_block(
    block_id: str,
    payload: CalendarBlockCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CalendarBlockResponse:
    block = db.get(CalendarBlock, block_id)
    if not block or block.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")
    block.title = payload.title
    block.block_type = payload.type
    block.weekday = payload.weekday
    block.start_time = payload.start_time
    block.end_time = payload.end_time
    block.repeat_rule = payload.repeat
    block.start_date = payload.start_date
    block.end_date = payload.end_date
    db.commit()
    db.refresh(block)
    return CalendarBlockResponse.model_validate(serialize_calendar_block(block))


@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block(
    block_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    block = db.get(CalendarBlock, block_id)
    if not block or block.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")
    db.delete(block)
    db.commit()

