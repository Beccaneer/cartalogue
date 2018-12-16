import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()

# Definition for User model


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

# Definition for Artist model


class Artist(Base):
    __tablename__ = 'artist'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    year_of_birth = Column(Integer)
    year_of_death = Column(Integer)
    country = Column(String(50))
    art_movement = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'yob': self.year_of_birth,
            'yod': self.year_of_death,
            'country': self.country,
            'movement': self.art_movement
        }

# Definition for artwork model


class Artwork(Base):
    __tablename__ = 'artwork'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    medium = Column(String(250))
    size = Column(String(80))
    year_created = Column(Integer)
    artist_id = Column(Integer, ForeignKey('artist.id'))
    artist = relationship(Artist)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'title': self.title,
            'medium': self.medium,
            'size': self.size,
            'year': self.year_created,
            'artist': self.artist.name
        }


engine = create_engine('sqlite:///art.db')

Base.metadata.create_all(engine)
