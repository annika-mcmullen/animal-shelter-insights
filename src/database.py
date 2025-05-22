# src/database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Animal(Base):
    __tablename__ = 'animals'

    # Core identifiers
    id = Column(Integer, primary_key=True)
    petfinder_id = Column(String(50), unique=True, nullable=False)
    organization_id = Column(String(50))

    # Basic info
    name = Column(String(100))
    species = Column(String(50))  # dog, cat, etc.
    breed_primary = Column(String(100))
    breed_secondary = Column(String(100))
    breed_mixed = Column(Boolean)
    breed_unknown = Column(Boolean)

    # Physical characteristics
    age = Column(String(20))  # baby, young, adult, senior
    gender = Column(String(20))
    size = Column(String(20))  # small, medium, large, xlarge
    coat = Column(String(50))
    color_primary = Column(String(50))
    color_secondary = Column(String(50))
    color_tertiary = Column(String(50))

    # Status and care
    status = Column(String(50))  # adoptable, adopted, found, etc.
    spayed_neutered = Column(Boolean)
    house_trained = Column(Boolean)
    declawed = Column(Boolean)
    special_needs = Column(Boolean)
    shots_current = Column(Boolean)

    # Behavioral info
    good_with_children = Column(Boolean)
    good_with_dogs = Column(Boolean)
    good_with_cats = Column(Boolean)

    # Descriptions and media
    description = Column(Text)
    photos = Column(JSON)  # Store as JSON array
    videos = Column(JSON)

    # Location
    city = Column(String(100))
    state = Column(String(50))
    postcode = Column(String(20))
    country = Column(String(50))

    # Timing data
    published_at = Column(DateTime)
    status_changed_at = Column(DateTime)
    distance = Column(Float)  # If search was location-based

    # Metadata
    scraped_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

    # Store raw JSON for reference
    raw_data = Column(JSON)


class Organization(Base):
    __tablename__ = 'organizations'

    id = Column(String(50), primary_key=True)  # Petfinder org ID
    name = Column(String(200))
    email = Column(String(100))
    phone = Column(String(50))
    website = Column(String(200))

    # Address
    address1 = Column(String(200))
    address2 = Column(String(200))
    city = Column(String(100))
    state = Column(String(50))
    postcode = Column(String(20))
    country = Column(String(50))

    # Details
    mission_statement = Column(Text)
    adoption_policy = Column(Text)
    adoption_url = Column(String(200))

    # Metadata
    scraped_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSON)


class DatabaseManager:
    def __init__(self, database_url: str = None):
        if not database_url:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///data/shelter_data.db')

        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        print("✅ Database tables created")

    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

    def save_animal(self, animal_data: dict):
        """Save animal data to database"""
        session = self.get_session()
        try:
            # Check if animal already exists
            existing = session.query(Animal).filter_by(
                petfinder_id=str(animal_data['id'])
            ).first()

            if existing:
                # Update existing record
                self._update_animal_from_data(existing, animal_data)
                existing.last_updated = datetime.utcnow()
                animal = existing
            else:
                # Create new record
                animal = self._create_animal_from_data(animal_data)
                session.add(animal)

            session.commit()
            return animal

        except Exception as e:
            session.rollback()
            print(f"❌ Error saving animal {animal_data.get('id')}: {e}")
            return None
        finally:
            session.close()

    def _create_animal_from_data(self, data: dict) -> Animal:
        """Convert Petfinder JSON to Animal model"""
        # Extract nested data safely
        breeds = data.get('breeds', {})
        colors = data.get('colors', {})
        attributes = data.get('attributes', {})
        environment = data.get('environment', {})
        contact = data.get('contact', {})
        address = contact.get('address', {})

        return Animal(
            petfinder_id=str(data['id']),
            organization_id=data.get('organization_id'),
            name=data.get('name'),
            species=data.get('species'),
            breed_primary=breeds.get('primary'),
            breed_secondary=breeds.get('secondary'),
            breed_mixed=breeds.get('mixed'),
            breed_unknown=breeds.get('unknown'),
            age=data.get('age'),
            gender=data.get('gender'),
            size=data.get('size'),
            coat=data.get('coat'),
            color_primary=colors.get('primary'),
            color_secondary=colors.get('secondary'),
            color_tertiary=colors.get('tertiary'),
            status=data.get('status'),
            spayed_neutered=attributes.get('spayed_neutered'),
            house_trained=attributes.get('house_trained'),
            declawed=attributes.get('declawed'),
            special_needs=attributes.get('special_needs'),
            shots_current=attributes.get('shots_current'),
            good_with_children=environment.get('children'),
            good_with_dogs=environment.get('dogs'),
            good_with_cats=environment.get('cats'),
            description=data.get('description'),
            photos=data.get('photos', []),
            videos=data.get('videos', []),
            city=address.get('city'),
            state=address.get('state'),
            postcode=address.get('postcode'),
            country=address.get('country'),
            published_at=datetime.fromisoformat(data['published_at'].replace('Z', '+00:00')) if data.get(
                'published_at') else None,
            status_changed_at=datetime.fromisoformat(data['status_changed_at'].replace('Z', '+00:00')) if data.get(
                'status_changed_at') else None,
            distance=data.get('distance'),
            raw_data=data
        )

    def _update_animal_from_data(self, animal: Animal, data: dict):
        """Update existing animal with new data"""
        # Update fields that might change
        animal.status = data.get('status')
        animal.description = data.get('description')
        animal.photos = data.get('photos', [])

        if data.get('status_changed_at'):
            animal.status_changed_at = datetime.fromisoformat(
                data['status_changed_at'].replace('Z', '+00:00')
            )

        animal.raw_data = data


# Initialize database
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    db = DatabaseManager()
    db.create_tables()
    print("Database setup complete!")