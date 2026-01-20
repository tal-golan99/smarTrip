"""
SQLAlchemy Models for SmartTrip Database Schema V2
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Date, DateTime, 
    SmallInteger, Boolean, ForeignKey, Enum, Index, CheckConstraint,
    event
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func
import enum

Base = declarative_base()


# ============================================
# ENUMS
# ============================================

class TripStatus(enum.Enum):
    """Trip availability status"""
    OPEN = "Open"
    GUARANTEED = "Guaranteed"
    LAST_PLACES = "Last Places"
    FULL = "Full"
    CANCELLED = "Cancelled"


class Gender(enum.Enum):
    """Guide gender"""
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class Continent(enum.Enum):
    """Geographic continents"""
    AFRICA = "Africa"
    ASIA = "Asia"
    EUROPE = "Europe"
    NORTH_AND_CENTRAL_AMERICA = "North & Central America"
    SOUTH_AMERICA = "South America"
    OCEANIA = "Oceania"
    ANTARCTICA = "Antarctica"


# TagCategory enum removed - category column dropped from tags table in V2 migration
# All tags are now theme tags; TYPE info is in trip_types table


class ReviewSource(enum.Enum):
    """Where the review came from"""
    WEBSITE = "Website"
    APP = "App"
    EMAIL = "Email"
    IMPORTED = "Imported"


# ============================================
# COMPANY MODEL (NEW)
# ============================================

class Company(Base):
    """
    Companies table - stores travel company/tour operator information.
    
    A company organizes and operates trip templates.
    One company can have many trip templates (1:N relationship).
    """
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    name_he = Column(String(255), nullable=False)
    description = Column(Text)
    description_he = Column(Text)
    logo_url = Column(String(500))
    website_url = Column(String(500))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    trip_templates = relationship('TripTemplate', back_populates='company', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'name_he': self.name_he,
            'nameHe': self.name_he,
            'description': self.description,
            'descriptionHe': self.description_he,
            'logoUrl': self.logo_url,
            'websiteUrl': self.website_url,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }


# ============================================
# EXISTING MODELS (UNCHANGED)
# ============================================

class Country(Base):
    """Countries table - stores destination countries"""
    __tablename__ = 'countries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    name_he = Column(String(100), nullable=False)
    continent = Column(Enum(Continent), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    template_countries = relationship('TripTemplateCountry', back_populates='country', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Country(id={self.id}, name='{self.name}', continent='{self.continent.value}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'nameHe': self.name_he,
            'continent': self.continent.value,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }


class Guide(Base):
    """Guides table - stores tour guide information"""
    __tablename__ = 'guides'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    name_he = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    gender = Column(Enum(Gender), nullable=False)
    age = Column(Integer)
    bio = Column(Text)
    bio_he = Column(Text)
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    trip_occurrences = relationship('TripOccurrence', back_populates='guide')
    
    def __repr__(self):
        return f"<Guide(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_he': self.name_he,
            'nameHe': self.name_he,
            'email': self.email,
            'phone': self.phone,
            'gender': self.gender.value,
            'age': self.age,
            'bio': self.bio,
            'bioHe': self.bio_he,
            'imageUrl': self.image_url,
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }


class TripType(Base):
    """Trip Types table - stores trip style categories"""
    __tablename__ = 'trip_types'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    name_he = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    trip_templates = relationship('TripTemplate', back_populates='trip_type')
    
    def __repr__(self):
        return f"<TripType(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'nameHe': self.name_he,
            'description': self.description,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }


class Tag(Base):
    """Tags table - stores trip theme tags

    Note: Category column was dropped in V2 migration.
    All tags are now theme tags.
    """
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    name_he = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    template_tags = relationship('TripTemplateTag', back_populates='tag', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'nameHe': self.name_he,
            'category': 'theme',  # V2: All tags are theme tags (backward compatibility)
            'description': self.description,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }


# ============================================
# TRIP TEMPLATE MODEL (REFACTORED FROM TRIPS)
# ============================================

class TripTemplate(Base):
    """
    Trip Templates table - stores the DEFINITION of a trip.
    
    This is the "what" of a trip - the route, description, base pricing.
    Specific scheduled instances are stored in TripOccurrences.
    
    Key changes from old trips table:
    - No start_date, end_date (moved to occurrences)
    - No status, spots_left (moved to occurrences)
    - No guide_id (moved to occurrences - guides can change per occurrence)
    - Added company_id (which company organizes this trip)
    - Added typical_duration_days
    - Added multi-country support via junction table
    """
    __tablename__ = 'trip_templates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic Info
    title = Column(String(255), nullable=False, index=True)
    title_he = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    description_he = Column(Text, nullable=False)
    short_description = Column(String(500))
    short_description_he = Column(String(500))
    image_url = Column(String(500))
    
    # Pricing (base/typical values - can be overridden in occurrences)
    base_price = Column(Numeric(10, 2), nullable=False)
    single_supplement_price = Column(Numeric(10, 2))
    
    # Duration
    typical_duration_days = Column(Integer, nullable=False)
    
    # Capacity (default - can be overridden in occurrences)
    default_max_capacity = Column(Integer, nullable=False)
    
    # Difficulty (1-5 scale)
    difficulty_level = Column(SmallInteger, nullable=False, index=True)
    
    # Foreign Keys
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='RESTRICT'), nullable=False, index=True)
    trip_type_id = Column(Integer, ForeignKey('trip_types.id', ondelete='RESTRICT'), nullable=True, index=True)
    
    # Primary country (for backward compatibility - main destination)
    primary_country_id = Column(Integer, ForeignKey('countries.id', ondelete='RESTRICT'), nullable=True, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Extensible properties (JSONB) - stores dynamic metadata without schema changes
    # Examples: packing_list, requirements (visas, vaccinations), type-specific attributes
    properties = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship('Company', back_populates='trip_templates')
    trip_type = relationship('TripType', back_populates='trip_templates', lazy='joined')
    primary_country = relationship('Country', foreign_keys=[primary_country_id])
    occurrences = relationship('TripOccurrence', back_populates='template', cascade='all, delete-orphan')
    template_tags = relationship('TripTemplateTag', back_populates='template', cascade='all, delete-orphan')
    template_countries = relationship('TripTemplateCountry', back_populates='template', cascade='all, delete-orphan')
    price_history = relationship('PriceHistory', back_populates='template', cascade='all, delete-orphan')
    reviews = relationship('Review', back_populates='template', cascade='all, delete-orphan')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('difficulty_level BETWEEN 1 AND 5', name='ck_difficulty_range'),
        CheckConstraint('typical_duration_days > 0', name='ck_duration_positive'),
        CheckConstraint('base_price >= 0', name='ck_base_price_positive'),
        Index('ix_trip_templates_company_type', 'company_id', 'trip_type_id'),
    )
    
    def __repr__(self):
        return f"<TripTemplate(id={self.id}, title='{self.title}')>"
    
    @property
    def countries(self):
        """Get list of all countries for this template"""
        return [tc.country for tc in self.template_countries]
    
    @property
    def tags(self):
        """Get list of all tags for this template"""
        return [tt.tag for tt in self.template_tags]
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'title': self.title,
            'titleHe': self.title_he,
            'description': self.description,
            'descriptionHe': self.description_he,
            'shortDescription': self.short_description,
            'shortDescriptionHe': self.short_description_he,
            'imageUrl': self.image_url,
            'basePrice': float(self.base_price) if self.base_price else None,
            'singleSupplementPrice': float(self.single_supplement_price) if self.single_supplement_price else None,
            'typicalDurationDays': self.typical_duration_days,
            'defaultMaxCapacity': self.default_max_capacity,
            'difficultyLevel': self.difficulty_level,
            'companyId': self.company_id,
            'tripTypeId': self.trip_type_id,
            'primaryCountryId': self.primary_country_id,
            'isActive': self.is_active,
            'properties': self.properties,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            data['company'] = self.company.to_dict() if self.company else None
            data['tripType'] = self.trip_type.to_dict() if self.trip_type else None
            data['primaryCountry'] = self.primary_country.to_dict() if self.primary_country else None
            data['countries'] = [c.to_dict() for c in self.countries]
            data['tags'] = [t.to_dict() for t in self.tags]
        
        return data


# ============================================
# TRIP OCCURRENCE MODEL (NEW)
# ============================================

class TripOccurrence(Base):
    """
    Trip Occurrences table - stores SPECIFIC SCHEDULED INSTANCES of trip templates.
    
    This is the "when" of a trip - specific dates, assigned guide, availability.
    The same TripTemplate can have many occurrences with different dates/guides.
    
    TODO: For production-grade concurrency control, spots_left should be replaced
    with a Bookings table where availability is computed as:
    (max_capacity - COUNT(confirmed_bookings)). This prevents race conditions
    when multiple users try to book simultaneously. Current implementation
    uses a simple Integer counter which is suitable for low-traffic scenarios.
    """
    __tablename__ = 'trip_occurrences'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    trip_template_id = Column(Integer, ForeignKey('trip_templates.id', ondelete='RESTRICT'), nullable=False, index=True)
    guide_id = Column(Integer, ForeignKey('guides.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Schedule
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    
    # Pricing (overrides - NULL means use template's base values)
    price_override = Column(Numeric(10, 2), nullable=True)
    single_supplement_override = Column(Numeric(10, 2), nullable=True)
    
    # Capacity (override - NULL means use template's default)
    max_capacity_override = Column(Integer, nullable=True)
    
    # Availability
    # TODO: See class docstring - spots_left should eventually be computed from a Bookings table
    spots_left = Column(Integer, nullable=False)
    # Note: status is VARCHAR in the database, not enum (for flexibility)
    status = Column(String(20), default='Open', nullable=False, index=True)
    
    # Image override (for seasonal variations)
    image_url_override = Column(String(500), nullable=True)
    
    # Additional notes for this specific occurrence
    notes = Column(Text)
    notes_he = Column(Text)
    
    # Extensible properties (JSONB) - stores occurrence-specific dynamic metadata
    # Examples: special_requirements, cabin_assignment, specific_equipment
    properties = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    template = relationship('TripTemplate', back_populates='occurrences', lazy='joined')
    guide = relationship('Guide', back_populates='trip_occurrences')
    reviews = relationship('Review', back_populates='occurrence')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('end_date >= start_date', name='ck_valid_date_range'),
        CheckConstraint('spots_left >= 0', name='ck_spots_left_positive'),
        Index('ix_trip_occurrences_dates', 'start_date', 'end_date'),
        Index('ix_trip_occurrences_template_dates', 'trip_template_id', 'start_date'),
        Index('ix_trip_occurrences_status_spots', 'status', 'spots_left'),  # For filtering available trips
        Index('ix_trip_occurrences_start_status', 'start_date', 'status'),  # For date + status filters
    )
    
    def __repr__(self):
        return f"<TripOccurrence(id={self.id}, template_id={self.trip_template_id}, dates={self.start_date} to {self.end_date})>"
    
    # ----------------------------------------
    # Hybrid Properties for DB-Level Queries
    # ----------------------------------------
    
    @hybrid_property
    def effective_price(self):
        """
        Returns the actual price for this occurrence.
        Uses price_override if set, otherwise falls back to template's base_price.
        """
        if self.price_override is not None:
            return self.price_override
        return self.template.base_price if self.template else None
    
    @effective_price.expression
    def effective_price(cls):
        """
        SQL expression for effective_price.
        Allows sorting/filtering by price at the database level.
        Usage: query.order_by(TripOccurrence.effective_price)
        """
        from sqlalchemy import case
        return case(
            (cls.price_override.isnot(None), cls.price_override),
            else_=select(TripTemplate.base_price).where(TripTemplate.id == cls.trip_template_id).correlate(cls).scalar_subquery()
        )
    
    @hybrid_property
    def effective_max_capacity(self):
        """Returns the actual max capacity for this occurrence."""
        if self.max_capacity_override is not None:
            return self.max_capacity_override
        return self.template.default_max_capacity if self.template else None
    
    @hybrid_property
    def effective_image_url(self):
        """Returns the image URL (override or template default)."""
        if self.image_url_override:
            return self.image_url_override
        return self.template.image_url if self.template else None
    
    @property
    def duration_days(self):
        """Calculate actual duration from dates"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None
    
    def to_dict(self, include_template=False):
        """Convert model to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'tripTemplateId': self.trip_template_id,
            'guideId': self.guide_id,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'price': float(self.effective_price) if self.effective_price else None,
            'priceOverride': float(self.price_override) if self.price_override else None,
            'singleSupplementOverride': float(self.single_supplement_override) if self.single_supplement_override else None,
            'maxCapacity': self.effective_max_capacity,
            'maxCapacityOverride': self.max_capacity_override,
            'spotsLeft': self.spots_left,
            'status': self.status,
            'imageUrl': self.effective_image_url,
            'imageUrlOverride': self.image_url_override,
            'notes': self.notes,
            'notesHe': self.notes_he,
            'properties': self.properties,
            'durationDays': self.duration_days,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_template and self.template:
            data['template'] = self.template.to_dict(include_relations=True)
        
        if self.guide:
            data['guide'] = self.guide.to_dict()
        
        return data


# ============================================
# JUNCTION TABLES
# ============================================

class TripTemplateTag(Base):
    """Junction table for TripTemplate <-> Tag many-to-many relationship"""
    __tablename__ = 'trip_template_tags'
    
    trip_template_id = Column(Integer, ForeignKey('trip_templates.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    template = relationship('TripTemplate', back_populates='template_tags')
    tag = relationship('Tag', back_populates='template_tags')
    
    __table_args__ = (
        Index('ix_trip_template_tags_tag', 'tag_id'),
    )
    
    def __repr__(self):
        return f"<TripTemplateTag(template_id={self.trip_template_id}, tag_id={self.tag_id})>"


class TripTemplateCountry(Base):
    """
    Junction table for TripTemplate <-> Country many-to-many relationship.
    
    Allows a single trip template to visit multiple countries.
    visit_order indicates the sequence of countries visited.
    days_in_country is optional - approximate time spent in each country.
    """
    __tablename__ = 'trip_template_countries'
    
    trip_template_id = Column(Integer, ForeignKey('trip_templates.id', ondelete='CASCADE'), primary_key=True)
    country_id = Column(Integer, ForeignKey('countries.id', ondelete='CASCADE'), primary_key=True)
    visit_order = Column(Integer, nullable=False, default=1)
    days_in_country = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    template = relationship('TripTemplate', back_populates='template_countries')
    country = relationship('Country', back_populates='template_countries')
    
    __table_args__ = (
        Index('ix_trip_template_countries_country', 'country_id'),
        Index('ix_trip_template_countries_order', 'trip_template_id', 'visit_order'),
    )
    
    def __repr__(self):
        return f"<TripTemplateCountry(template_id={self.trip_template_id}, country_id={self.country_id}, order={self.visit_order})>"


# ============================================
# PRICE HISTORY (NEW)
# ============================================

class PriceHistory(Base):
    """
    Price History table - tracks price changes for analytics.
    
    Records every change to base_price on TripTemplate.
    Useful for:
    - Auditing price changes
    - Analyzing pricing trends
    - Understanding seasonal pricing patterns
    """
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trip_template_id = Column(Integer, ForeignKey('trip_templates.id', ondelete='CASCADE'), nullable=False, index=True)
    old_price = Column(Numeric(10, 2), nullable=True)
    new_price = Column(Numeric(10, 2), nullable=False)
    change_reason = Column(String(255), nullable=True)
    changed_by = Column(String(100), nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    template = relationship('TripTemplate', back_populates='price_history')
    
    __table_args__ = (
        Index('ix_price_history_template_date', 'trip_template_id', 'changed_at'),
    )
    
    def __repr__(self):
        return f"<PriceHistory(template_id={self.trip_template_id}, old={self.old_price}, new={self.new_price})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'tripTemplateId': self.trip_template_id,
            'oldPrice': float(self.old_price) if self.old_price else None,
            'newPrice': float(self.new_price) if self.new_price else None,
            'changeReason': self.change_reason,
            'changedBy': self.changed_by,
            'changedAt': self.changed_at.isoformat() if self.changed_at else None,
        }


# ============================================
# REVIEWS (NEW)
# ============================================

class Review(Base):
    """
    Reviews table - stores user reviews for trips.
    
    Reviews are linked to TripTemplate (the trip being reviewed).
    Optionally linked to a specific TripOccurrence if the reviewer
    attended a specific departure date.
    
    Features:
    - 1-5 star rating
    - Optional text review
    - Moderation status
    - Source tracking
    """
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # What is being reviewed
    trip_template_id = Column(Integer, ForeignKey('trip_templates.id', ondelete='CASCADE'), nullable=False, index=True)
    trip_occurrence_id = Column(Integer, ForeignKey('trip_occurrences.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Reviewer info (can be anonymous)
    reviewer_name = Column(String(100), nullable=True)
    reviewer_email = Column(String(255), nullable=True)
    is_anonymous = Column(Boolean, default=False, nullable=False)
    
    # Review content
    rating = Column(SmallInteger, nullable=False)  # 1-5 stars
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=True)
    content_he = Column(Text, nullable=True)
    
    # Metadata
    source = Column(Enum(ReviewSource), default=ReviewSource.WEBSITE, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)  # Verified purchase
    is_approved = Column(Boolean, default=False, nullable=False, index=True)  # Moderation
    is_featured = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    travel_date = Column(Date, nullable=True)  # When they traveled (if known)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    template = relationship('TripTemplate', back_populates='reviews')
    occurrence = relationship('TripOccurrence', back_populates='reviews')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('rating BETWEEN 1 AND 5', name='ck_rating_range'),
        Index('ix_reviews_template_approved', 'trip_template_id', 'is_approved'),
        Index('ix_reviews_rating', 'rating'),
    )
    
    def __repr__(self):
        return f"<Review(id={self.id}, template_id={self.trip_template_id}, rating={self.rating})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'tripTemplateId': self.trip_template_id,
            'tripOccurrenceId': self.trip_occurrence_id,
            'reviewerName': self.reviewer_name if not self.is_anonymous else 'Anonymous',
            'isAnonymous': self.is_anonymous,
            'rating': self.rating,
            'title': self.title,
            'content': self.content,
            'contentHe': self.content_he,
            'source': self.source.value,
            'isVerified': self.is_verified,
            'isApproved': self.is_approved,
            'isFeatured': self.is_featured,
            'travelDate': self.travel_date.isoformat() if self.travel_date else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }


# ============================================
# BACKWARD COMPATIBILITY VIEW (for migration period)
# ============================================

# Note: This is a conceptual view definition.
# Actual view creation happens in migration script.
TRIPS_COMPAT_VIEW_SQL = """
CREATE OR REPLACE VIEW trips_compat AS
SELECT 
    o.id,
    tt.title, 
    tt.title_he,
    tt.description, 
    tt.description_he,
    COALESCE(o.image_url_override, tt.image_url) as image_url,
    o.start_date, 
    o.end_date,
    COALESCE(o.price_override, tt.base_price) as price,
    COALESCE(o.single_supplement_override, tt.single_supplement_price) as single_supplement_price,
    COALESCE(o.max_capacity_override, tt.default_max_capacity) as max_capacity,
    o.spots_left, 
    o.status,
    tt.difficulty_level,
    tt.primary_country_id as country_id, 
    o.guide_id, 
    tt.trip_type_id, 
    tt.company_id,
    o.created_at, 
    o.updated_at
FROM trip_occurrences o
JOIN trip_templates tt ON o.trip_template_id = tt.id
WHERE tt.is_active = TRUE;
"""


# ============================================
# EVENT LISTENERS (for price history tracking)
# ============================================

@event.listens_for(TripTemplate.base_price, 'set')
def track_price_change(target, value, oldvalue, initiator):
    """
    Automatically record price changes to price_history.
    
    Note: This listener fires on attribute set, but the actual
    INSERT to price_history should happen in the application layer
    to have access to session and additional context (changed_by, reason).
    """
    # This is a placeholder - actual implementation should be in service layer
    # to properly handle session management and additional context
    pass
