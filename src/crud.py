from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import DoctorORM, UserORM, RoomORM
from model import DoctorItemUpdate, UserItemUpdate, DoctorItemCreate, UserItemCreate, RoomItemCreate
from auth import get_password_hash
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


async def create_doctor(db: AsyncSession, data: DoctorItemCreate) -> DoctorORM:
    """
        Create a new doctor in the database.

        Args:
            db: Async database session
            data: Validated doctor creation data

        Returns:
            The newly created doctor record

        Raises:
            HTTPException: If there's a database integrity error
                - 409 Conflict for duplicate entries or invalid references
        """
    hashed_password = get_password_hash(data.password)
    doctor = DoctorORM(name=data.name, surname=data.surname, age=data.age, specialization=data.specialization,
                       category=data.category, password=hashed_password)
    try:
        db.add(doctor)
        await db.commit()
        await db.refresh(doctor)
    except IntegrityError as e:
        await db.rollback()

        error_msg = "Database integrity error"
        if "unique constraint" in str(e).lower():
            error_msg = "Duplicate entry. Doctor with these details already exists"
        elif "foreign key constraint" in str(e).lower():
            error_msg = "Invalid reference in foreign key"

        raise HTTPException(
            status_code=409,
            detail=error_msg
        )
    return doctor


async def get_doctors(db: AsyncSession, page: int, size: int) -> list[DoctorORM]:
    """
        Retrieve a paginated list of doctors from the database.

        Args:
            db (AsyncSession): The asynchronous database session.
            page (int): The page number to retrieve (starting from 1).
            size (int): The number of records per page.

        Returns:
            List[DoctorORM]: A list of DoctorORM objects corresponding to the requested page.

        Example:
            doctors = await get_doctors(db_session, page=2, size=10)
        """
    result = await db.execute(select(DoctorORM).order_by(DoctorORM.name.asc()).offset((page - 1) * size).limit(size))
    doctors = result.scalars().all()
    return doctors


async def get_doctor(db: AsyncSession, doctor_id: UUID) -> DoctorORM:
    """
        Retrieve a doctor by their ID from the database.

        Args:
            db: Async database session
            doctor_id: UUID of the doctor to retrieve

        Returns:
            DoctorORM instance if found, None otherwise
        """
    result = await db.execute(select(DoctorORM).filter(DoctorORM.id == doctor_id))
    doctor = result.scalars().first()
    return doctor


async def update_doctor_dump(db: AsyncSession, doctor_id: UUID, doctor_update: DoctorItemUpdate) -> DoctorORM | None:
    """
        Update a doctor's information in the database.

        Args:
            db: Async database session
            doctor_id: ID of the doctor to update
            doctor_update: Validated update data (Pydantic model)

        Returns:
            Updated DoctorORM instance if found and updated, None if doctor not found

        Raises:
            HTTPException: If there's a database error during update
        """
    db_doctor = await get_doctor(db, doctor_id)
    if not db_doctor:
        return None

    update_data = doctor_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_doctor, field, value)

    db.add(db_doctor)
    await db.commit()
    await db.refresh(db_doctor)
    return db_doctor


async def delete_doctor(db: AsyncSession, doctor_id: UUID)-> DoctorORM | None:
    """
        Delete a doctor record from the database by ID.

        Args:
            db: Async database session
            doctor_id: UUID string identifying the doctor to delete

        Returns:
            The deleted DoctorORM instance if found and deleted,
            None if no doctor with given ID exists

        Raises:
            HTTPException:
                - 404 Not Found if doctor doesn't exist (optional)
                - 500 Internal Server Error if database operation fails
        """
    doctor = await get_doctor(db, doctor_id)
    if not doctor:
        return None
    await db.delete(doctor)
    await db.commit()
    return doctor


async def create_user(db: AsyncSession, data: UserItemCreate):
    hashed_password = get_password_hash(data.password)
    user = UserORM(name=data.name, surname=data.surname, email=data.email, age=data.age,
                       phone=data.phone, role=data.role, password=hashed_password, disabled=False)
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    except IntegrityError as e:
        await db.rollback()

        error_msg = "Database integrity error"
        if "unique constraint" in str(e).lower():
            error_msg = "Duplicate entry. User with these details already exists"
        elif "foreign key constraint" in str(e).lower():
            error_msg = "Invalid reference in foreign key"

        raise HTTPException(
            status_code=409,
            detail=error_msg
        )
    return user


async def get_users(db: AsyncSession, page: int, size: int) -> list[UserORM]:
    result = await db.execute(select(UserORM).order_by(UserORM.name.asc()).offset((page - 1) * size).limit(size))
    users = result.scalars().all()
    return users


async def get_user(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(UserORM).filter(UserORM.id == user_id))
    user = result.scalars().first()
    return user


async def update_user_dump(db: AsyncSession, user_id: UUID, user_update: UserItemUpdate):
    db_user = await get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: UUID):
    user = await get_user(db, user_id)
    if not user:
        return None
    await db.delete(user)
    await db.commit()
    return user


async def create_room(db: AsyncSession, data: RoomItemCreate):
    room = RoomORM(number=data.number)
    try:
        db.add(room)
        await db.commit()
        await db.refresh(room)
    except IntegrityError as e:
        await db.rollback()

        error_msg = "Database integrity error"
        if "unique constraint" in str(e).lower():
            error_msg = "Duplicate entry. User with these details already exists"
        elif "foreign key constraint" in str(e).lower():
            error_msg = "Invalid reference in foreign key"

        raise HTTPException(
            status_code=409,
            detail=error_msg
        )
    return room