from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db

security = HTTPBearer()

from app.models import Notification, Redemption, Report, Reward, Role, User, WasteType
from app.schemas import (
    LoginRequest, MessageResponse, NotificationResponse, RedeemRequest,
    RedeemResponse, RedemptionResponse, ReportCreate, ReportResponse,
    RewardResponse, RoleResponse, TokenResponse, UserCreate,
    UserProfileResponse, UserResponse, WasteTypeResponse,
)
from app.security import (
    create_access_token, decode_access_token, hash_password, verify_password,
)

router = APIRouter()


def get_current_user(
    db: Session = Depends(get_db),
    token_data: str = Depends(security),
):
    payload = decode_access_token(token_data.credentials)
    if payload is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")
    return user


@router.post("/auth/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    role_name = user.role.name if user.role else "user"
    try:
        token = create_access_token({"sub": str(user.id), "role": role_name})
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Error creating token: {e}",
        )
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=UserProfileResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/roles", response_model=list[RoleResponse])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    user_role = db.query(Role).filter(Role.name == "user").first()
    if not user_role:
        raise HTTPException(400, "Default role not found. Run setup first.")
    if db.query(User).filter((User.email == data.email) | (User.username == data.username)).first():
        raise HTTPException(400, "Email or username already exists")
    user = User(
        email=data.email, username=data.username,
        hashed_password=hash_password(data.password), full_name=data.full_name,
        role_id=user_role.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/waste-types", response_model=list[WasteTypeResponse])
def list_waste_types(db: Session = Depends(get_db)):
    return db.query(WasteType).all()


@router.get("/reports", response_model=list[ReportResponse])
def list_reports(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Report)
    if status_filter:
        q = q.filter(Report.status == status_filter)
    return q.order_by(Report.created_at.desc()).all()


@router.get("/reports/mine", response_model=list[ReportResponse])
def my_reports(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Report)
        .filter(Report.user_id == current_user.id)
        .order_by(Report.created_at.desc())
        .all()
    )


@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    waste_type = db.query(WasteType).filter(WasteType.id == data.waste_type_id).first()
    if not waste_type:
        raise HTTPException(400, "Invalid waste type")
    report = Report(
        user_id=current_user.id,
        waste_type_id=data.waste_type_id,
        title=data.title, description=data.description,
        latitude=data.latitude, longitude=data.longitude,
        address=data.address, estimated_quantity=data.estimated_quantity,
        status="pending",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(report_id: str, db: Session = Depends(get_db)):
    from uuid import UUID
    report = db.query(Report).filter(Report.id == UUID(report_id)).first()
    if not report:
        raise HTTPException(404, "Report not found")
    return report


@router.get("/rewards", response_model=list[RewardResponse])
def list_rewards(db: Session = Depends(get_db)):
    return db.query(Reward).filter(Reward.is_active == True).all()


@router.post("/rewards/redeem", response_model=RedeemResponse)
def redeem_reward(
    data: RedeemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reward = db.query(Reward).filter(Reward.id == data.reward_id, Reward.is_active == True).first()
    if not reward:
        raise HTTPException(404, "Reward not found")
    if reward.stock is not None and reward.stock <= 0:
        raise HTTPException(400, "Reward out of stock")
    if current_user.points < reward.points_cost:
        raise HTTPException(400, "Insufficient points")

    redemption = Redemption(
        user_id=current_user.id, reward_id=reward.id,
        points_spent=reward.points_cost, status="approved",
    )
    current_user.points -= reward.points_cost
    if reward.stock is not None:
        reward.stock -= 1

    db.add(redemption)
    db.commit()
    db.refresh(redemption)

    return RedeemResponse(
        message=f"Redeemed {reward.name}",
        points_spent=reward.points_cost,
        remaining_points=current_user.points,
    )


@router.get("/redemptions", response_model=list[RedemptionResponse])
def my_redemptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = (
        db.query(Redemption, Reward.name)
        .join(Reward, Redemption.reward_id == Reward.id)
        .filter(Redemption.user_id == current_user.id)
        .order_by(Redemption.created_at.desc())
        .all()
    )
    return [
        RedemptionResponse(
            id=r.id, reward_id=r.reward_id, reward_name=name,
            points_spent=r.points_spent, status=r.status,
            created_at=r.created_at,
        )
        for r, name in results
    ]


@router.get("/notifications", response_model=list[NotificationResponse])
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )


@router.post("/notifications/{notification_id}/read", response_model=MessageResponse)
def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from uuid import UUID
    n = (
        db.query(Notification)
        .filter(
            Notification.id == UUID(notification_id),
            Notification.user_id == current_user.id,
        )
        .first()
    )
    if not n:
        raise HTTPException(404, "Notification not found")
    n.is_read = True
    db.commit()
    return MessageResponse(message="Notification marked as read")


@router.post("/setup", response_model=MessageResponse)
def setup(db: Session = Depends(get_db)):
    if db.query(Role).first():
        return MessageResponse(message="Already initialized")
    from uuid import uuid4
    admin_role = Role(id=uuid4(), name="admin", description="Admin")
    user_role = Role(id=uuid4(), name="user", description="User")
    moderator_role = Role(id=uuid4(), name="moderator", description="Moderator")
    db.add_all([admin_role, user_role, moderator_role])
    db.flush()
    admin_user = User(
        id=uuid4(), email="admin@ecocycle.app", username="admin",
        hashed_password=hash_password("admin123"), full_name="Admin",
        role_id=admin_role.id, is_active=True, is_verified=True,
    )
    db.add(admin_user)
    types = [
        WasteType(id=uuid4(), name="Plastico", points_per_report=10, points_per_kilo=2),
        WasteType(id=uuid4(), name="Vidrio", points_per_report=15, points_per_kilo=3),
        WasteType(id=uuid4(), name="Papel/Carton", points_per_report=10, points_per_kilo=1),
        WasteType(id=uuid4(), name="Metal", points_per_report=20, points_per_kilo=5),
        WasteType(id=uuid4(), name="Organico", points_per_report=8, points_per_kilo=1),
    ]
    db.add_all(types)
    db.commit()
    return MessageResponse(message="Database initialized")
