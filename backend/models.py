from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, Boolean, Float, Date
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"


    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    require_password_change = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemSettings(Base):
    __tablename__ = "system_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(Text, nullable=False) # Encrypted content
    is_encrypted = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow)


class CachedImage(Base):
    __tablename__ = "cached_images"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, unique=True, nullable=False, index=True)
    local_path = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    cached_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    source = Column(String, nullable=True) # trakt, tmdb
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)


class MediaItem(Base):
    __tablename__ = "media_items"

    id = Column(Integer, primary_key=True, index=True)
    full_path = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    year = Column(Integer, nullable=True)
    media_type = Column(String, nullable=True) # 'movie' or 'tv'
    size_bytes = Column(BigInteger, default=0)
    
    # IDs
    tmdb_id = Column(Integer, nullable=True, index=True)
    imdb_id = Column(String, nullable=True, index=True)
    
    # Metadata (Stored permanently)
    poster_url = Column(String, nullable=True) # This will be the PROXY URL (or raw if proxying fails)
    poster_cached_at = Column(DateTime, nullable=True)
    
    release_date = Column(Date, nullable=True) # Full release date (YYYY-MM-DD)
    overview = Column(String, nullable=True)
    rating = Column(Float, nullable=True) # Trakt rating 0-10
    genres = Column(String, nullable=True) # JSON list or comma-separated
    certification = Column(String, nullable=True) # e.g. "PG-13"
    runtime = Column(Integer, nullable=True) # Minutes
    tagline = Column(String, nullable=True)
    trailer_url = Column(String, nullable=True)
    homepage = Column(String, nullable=True)
    status = Column(String, nullable=True)
    network = Column(String, nullable=True)
    aired_episodes = Column(Integer, nullable=True)
    
    # Technical Metadata from Source File (JSON)
    source_metadata = Column(Text, nullable=True) 

    # Normalized Metadata (Queries)
    resolution = Column(String, nullable=True, index=True)
    codec = Column(String, nullable=True, index=True)
    source = Column(String, nullable=True, index=True)
    audio = Column(String, nullable=True, index=True)
    hdr = Column(String, nullable=True, index=True)
    is_remux = Column(Boolean, default=False, index=True) 
    
    enrichment_status = Column(String, default='pending', index=True) # pending, success, failed
    enrichment_retry_count = Column(Integer, default=0) 
    priority = Column(Integer, default=0, index=True) # 0=normal, 10=high (UI requested) 

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class CopyJob(Base):
    __tablename__ = "copy_jobs"

    id = Column(Integer, primary_key=True, index=True)
    source_path = Column(String, nullable=False)
    destination_path = Column(String, nullable=False)
    status = Column(String, nullable=False, default="queued")  # queued, processing, completed, failed, cancelled
    priority = Column(Integer, default=1, index=True)  # 0=low, 1=normal, 2=high
    progress_percent = Column(Integer, default=0)
    total_size_bytes = Column(BigInteger, default=0)
    copied_size_bytes = Column(BigInteger, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class StorageStats(Base):
    __tablename__ = "storage_stats"

    source = Column(String, primary_key=True)  # 'zurg' or 'harddrive'
    total_size = Column(BigInteger, default=0)
    used_size = Column(BigInteger, default=0)
    free_size = Column(BigInteger, default=0)
    percent = Column(Float, default=0.0)
    file_count = Column(Integer, default=0)
    folder_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

