from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Artist, Artwork, Base, User

engine = create_engine('sqlite:///art.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Users creation

user1 = User(
    email='test123@gmail.com',
    picture="""https://lh3.googleusercontent.com/
             -6jXvJsUFLfE/AAAAAAAAAAI/AAAAAAAAAAA/Xom8hrDa6bc/photo.jpg"""
)
session.add(user1)
session.commit()

user2 = User(
    email='test@gmail.com',
    picture="""https://lh3.googleusercontent.com
             /-6jXvJsUFLfE/AAAAAAAAAAI/AAAAAAAAAAA/Xom8hrDa6bc/photo.jpg"""
)
session.add(user2)
session.commit()

# Mondrian and associated artwork creation

artist1 = Artist(
    name="Piet Mondrian",
    year_of_birth=1872,
    year_of_death=1944,
    country="Netherlands",
    art_movement="De Stijl",
    user=user1
)

session.add(artist1)
session.commit()

artwork1 = Artwork(
    title="Composition with Red Blue and Yellow",
    medium="oil",
    size="23.4in x 23.4in",
    year_created=1929,
    artist=artist1,
    user=user1
)

session.add(artwork1)
session.commit()

artwork2 = Artwork(
    title="Broadway Boogie Woogie",
    medium="oil",
    size="50in x 50in",
    year_created=1943,
    artist=artist1,
    user=user1
)

session.add(artwork2)
session.commit()

# Picasso and associated artwork creation

artist2 = Artist(
    name="Pablo Picasso",
    year_of_birth=1881,
    year_of_death=1973,
    country="Spain",
    art_movement="Cubism",
    user=user1
)

session.add(artist2)
session.commit()

artwork3 = Artwork(
    title="Les Demoiselles d'Avignon",
    medium="oil",
    size="96in x 92in",
    year_created=1907,
    artist=artist2,
    user=user1
)

session.add(artwork3)
session.commit()

artwork4 = Artwork(
    title="Girl before a Mirror",
    medium="oil",
    size="63.9in x 51.3in",
    year_created=1932,
    artist=artist2,
    user=user1
)

session.add(artwork4)
session.commit()

# Rodin and associated artwork creation

artist3 = Artist(
    name="Auguste Rodin",
    year_of_birth=1840,
    year_of_death=1917,
    country="France",
    art_movement="Symbolism",
    user=user2
)

session.add(artist3)
session.commit()

artwork5 = Artwork(
    title="The Kiss",
    medium="marble",
    size="71.5in x 44.3in x 46in",
    year_created=1882,
    artist=artist3,
    user=user2
)

session.add(artwork5)
session.commit()

artwork6 = Artwork(
    title="The Age of Bronze",
    medium="bronze",
    size="lifesize",
    year_created=1877,
    artist=artist3,
    user=user2
)

session.add(artwork6)
session.commit()
