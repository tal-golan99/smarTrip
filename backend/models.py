"""
SQLAlchemy Models for SmartTrip Database Schema
Normalized to 3NF with Foreign Keys and Constraints
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Date, DateTime, 
    SmallInteger, Boolean, ForeignKey, Enum, Index
)
from sqlalchemy.orm import relationship, declarative_base
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


class TagCategory(enum.Enum):
    """Tag categories - Type vs Theme"""
    TYPE = "Type"  # The style of the trip (e.g., Safari, Cruise, Hiking)
    THEME = "Theme"  # The content/focus of the trip (e.g., Wildlife, Culture, Food)


# ============================================
# MODELS
# ============================================

class Country(Base):
    """Countries table - stores destination countries"""
    __tablename__ = 'countries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    name_he = Column(String(100), nullable=False)  # Hebrew name
    continent = Column(Enum(Continent), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    trips = relationship('Trip', back_populates='country', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Country(id={self.id}, name='{self.name}', continent='{self.continent.value}')>"
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
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
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    gender = Column(Enum(Gender), nullable=False)
    age = Column(Integer)
    bio = Column(Text)  # Biography in English
    bio_he = Column(Text)  # Biography in Hebrew
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    trips = relationship('Trip', back_populates='guide')
    
    def __repr__(self):
        return f"<Guide(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
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


class Tag(Base):
    """Tags table - stores trip type/category tags"""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    name_he = Column(String(100), nullable=False)  # Hebrew name
    description = Column(Text)
    category = Column(Enum(TagCategory), nullable=False, index=True)  # TYPE or THEME
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    trip_tags = relationship('TripTag', back_populates='tag', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', category='{self.category.value}')>"
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'nameHe': self.name_he,
            'description': self.description,
            'category': self.category.value,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }


class Trip(Base):
    """Trips table - stores organized tour information"""
    __tablename__ = 'trips'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    title_he = Column(String(255), nullable=False)  # Hebrew title
    description = Column(Text, nullable=False)
    description_he = Column(Text, nullable=False)  # Hebrew description
    image_url = Column(String(500))
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)  # Base price in ILS or USD
    single_supplement_price = Column(Numeric(10, 2))
    max_capacity = Column(Integer, nullable=False)
    spots_left = Column(Integer, nullable=False)
    status = Column(Enum(TripStatus), default=TripStatus.OPEN, nullable=False, index=True)
    difficulty_level = Column(SmallInteger, nullable=False, index=True)  # 1=Easy, 2=Moderate, 3=Hard
    country_id = Column(Integer, ForeignKey('countries.id', ondelete='RESTRICT'), nullable=False, index=True)
    guide_id = Column(Integer, ForeignKey('guides.id', ondelete='RESTRICT'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    country = relationship('Country', back_populates='trips')
    guide = relationship('Guide', back_populates='trips')
    trip_tags = relationship('TripTag', back_populates='trip', cascade='all, delete-orphan')
    
    # Additional indexes for query optimization
    __table_args__ = (
        Index('ix_trips_dates', 'start_date', 'end_date'),
    )
    
    def __repr__(self):
        return f"<Trip(id={self.id}, title='{self.title}', status='{self.status.value}')>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'title': self.title,
            'titleHe': self.title_he,
            'description': self.description,
            'descriptionHe': self.description_he,
            'imageUrl': self.image_url,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'price': float(self.price) if self.price else None,
            'singleSupplementPrice': float(self.single_supplement_price) if self.single_supplement_price else None,
            'maxCapacity': self.max_capacity,
            'spotsLeft': self.spots_left,
            'status': self.status.value,
            'difficultyLevel': self.difficulty_level,
            'countryId': self.country_id,
            'guideId': self.guide_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            data['country'] = self.country.to_dict() if self.country else None
            data['guide'] = self.guide.to_dict() if self.guide else None
            data['tags'] = [tt.tag.to_dict() for tt in self.trip_tags]
        
        return data


class TripTag(Base):
    """TripTags junction table - Many-to-Many relationship between Trips and Tags"""
    __tablename__ = 'trip_tags'
    
    trip_id = Column(Integer, ForeignKey('trips.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    trip = relationship('Trip', back_populates='trip_tags')
    tag = relationship('Tag', back_populates='trip_tags')
    
    # Index for reverse lookups
    __table_args__ = (
        Index('ix_trip_tags_tag_id', 'tag_id'),
    )
    
    def __repr__(self):
        return f"<TripTag(trip_id={self.trip_id}, tag_id={self.tag_id})>"


