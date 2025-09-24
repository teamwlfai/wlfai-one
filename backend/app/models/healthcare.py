"""
Healthcare-specific models for patients, providers, appointments, and facilities
"""

from datetime import date
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    DateTime,
    Date,
    Text,
    Numeric,
    ForeignKey,
    Enum,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel
from .enums import Gender, PatientStatus, ProviderStatus


class Patient(BaseModel):
    """Patient records with healthcare information"""

    __tablename__ = "patients"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    mrn = Column(String(100), nullable=False)  # Medical Record Number
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    phone = Column(String(50))
    email = Column(String(255))
    address = Column(JSONB)
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(50))
    insurance_info = Column(JSONB)
    preferences = Column(JSONB, default=dict)  # Language, communication method
    status = Column(Enum(PatientStatus), nullable=False, default=PatientStatus.ACTIVE)
    consent_ai_communication = Column(Boolean, default=False, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint("org_id", "mrn"),
        Index("idx_patient_org_name", "org_id", "last_name", "first_name"),
        Index("idx_patient_phone", "phone"),
        Index("idx_patient_email", "email"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="patients")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    appointments = relationship("Appointment", back_populates="patient")
    communications = relationship("Communication", back_populates="patient")
    interactions = relationship("AgentInteraction", back_populates="patient")


class Provider(BaseModel):
    """Healthcare providers (doctors, nurses, therapists)"""

    __tablename__ = "providers"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialty = Column(String(100))
    npi_number = Column(String(20), unique=True)
    license_number = Column(String(50))
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"))
    schedule = Column(JSONB, default=dict)  # Availability, working hours
    accepts_new_patients = Column(Boolean, default=True, nullable=False)
    status = Column(Enum(ProviderStatus), nullable=False, default=ProviderStatus.ACTIVE)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        Index("idx_provider_org_specialty", "org_id", "specialty"),
        Index("idx_provider_npi", "npi_number"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="providers")
    location = relationship("Location", back_populates="providers")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    appointments = relationship("Appointment", back_populates="provider")


class Department(BaseModel):
    """Hospital/clinic departments"""

    __tablename__ = "departments"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20))
    description = Column(Text)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    settings = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("org_id", "name"),
        Index("idx_department_org_active", "org_id", "is_active"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="departments")
    manager = relationship("User")
    appointments = relationship("Appointment", back_populates="department")


class FacilityType(BaseModel):
    """Types of healthcare facilities"""

    __tablename__ = "facility_types"

    name = Column(
        String(100), unique=True, nullable=False
    )  # Clinic, Hospital, Imaging Center
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    facilities = relationship("Facility", back_populates="facility_type")


class Location(BaseModel):
    """Physical locations for facilities and providers"""

    __tablename__ = "locations"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(JSONB, nullable=False)
    phone = Column(String(50))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    timezone = Column(String(50), default="UTC")
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("idx_location_org_active", "org_id", "is_active"),
        Index("idx_location_coordinates", "latitude", "longitude"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="locations")
    facilities = relationship("Facility", back_populates="location")
    providers = relationship("Provider", back_populates="location")


class Facility(BaseModel):
    """Healthcare facilities (clinics, hospitals, imaging centers)"""

    __tablename__ = "facilities"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(200), nullable=False)
    facility_type_id = Column(
        UUID(as_uuid=True), ForeignKey("facility_types.id"), nullable=False
    )
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    operating_hours = Column(JSONB, default=dict)
    contact_info = Column(JSONB)
    capacity = Column(Integer)
    amenities = Column(JSONB, default=list)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("idx_facility_org_type", "org_id", "facility_type_id"),
        Index("idx_facility_location", "location_id"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="facilities")
    facility_type = relationship("FacilityType", back_populates="facilities")
    location = relationship("Location", back_populates="facilities")
    appointments = relationship("Appointment", back_populates="facility")


class AppointmentType(BaseModel):
    """Types of appointments (checkup, follow-up, etc.)"""

    __tablename__ = "appointment_types"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(100), nullable=False)  # Checkup, Follow-up, Televisit
    description = Column(Text)
    default_duration = Column(Integer, default=30)  # Minutes
    default_cost = Column(Numeric(10, 2))
    color_code = Column(String(7))  # Hex color
    allows_online_booking = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (UniqueConstraint("org_id", "name"),)

    # Relationships
    organization = relationship("Organization", back_populates="appointment_types")
    appointments = relationship("Appointment", back_populates="appointment_type")


class AppointmentStatus(BaseModel):
    """Status values for appointments"""

    __tablename__ = "appointment_statuses"

    name = Column(
        String(100), unique=True, nullable=False
    )  # Scheduled, Confirmed, Completed
    color_code = Column(String(7))
    is_final = Column(Boolean, default=False, nullable=False)
    requires_confirmation = Column(Boolean, default=False, nullable=False)

    # Relationships
    appointments = relationship("Appointment", back_populates="status")


class Appointment(BaseModel):
    """Patient appointments with providers"""

    __tablename__ = "appointments"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    confirmation_code = Column(String(20), unique=True, nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    facility_id = Column(
        UUID(as_uuid=True), ForeignKey("facilities.id"), nullable=False
    )
    appointment_type_id = Column(
        UUID(as_uuid=True), ForeignKey("appointment_types.id"), nullable=False
    )
    status_id = Column(
        UUID(as_uuid=True), ForeignKey("appointment_statuses.id"), nullable=False
    )
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30)
    reason_for_visit = Column(Text)
    notes = Column(Text)
    provider_notes = Column(Text)
    metadata = Column(JSONB, default=dict)  # Telemedicine link, room number
    checked_in_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    cancellation_reason = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        Index("idx_appointment_org_date", "org_id", "scheduled_time"),
        Index("idx_appointment_patient", "patient_id", "scheduled_time"),
        Index("idx_appointment_provider", "provider_id", "scheduled_time"),
        Index("idx_appointment_confirmation", "confirmation_code"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
    provider = relationship("Provider", back_populates="appointments")
    department = relationship("Department", back_populates="appointments")
    facility = relationship("Facility", back_populates="appointments")
    appointment_type = relationship("AppointmentType", back_populates="appointments")
    status = relationship("AppointmentStatus", back_populates="appointments")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    communications = relationship("Communication", back_populates="appointment")
    workflow_executions = relationship(
        "WorkflowExecution", back_populates="appointment"
    )
