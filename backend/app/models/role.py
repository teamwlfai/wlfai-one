from sqlalchemy import Table, Column, Integer, String, MetaData, DateTime, func, Boolean

metadata = MetaData()

roles = Table(
    "roles",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, unique=True, index=True, nullable=False),
    Column("description", String, nullable=True),
    # 🔹 Audit Fields
    Column("created_by", Integer, nullable=True),  # user_id of creator
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
    Column("updated_by", Integer, nullable=True),  # user_id of updater
    Column(
        "updated_at",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    ),
    # 🔹 Active flag
    Column("is_active", Boolean, nullable=False, server_default="true"),
)
