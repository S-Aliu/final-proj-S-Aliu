from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import College, Region, Base, User
engine = create_engine('sqlite:///collegeswithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

User1 = User(name="Laura Slide", email="lauraswags4@gmail.com",
             picture='https://lh3.googleusercontent.com/a-/AAuE7mD_BnB0srAZwYDWQmWz2oPZ6H5CEpB0-iNxcpk5=s120')
session.add(User1)
session.commit()

# West Region
West = Region(name = "West", image_region = "west.jpg")
session.add(West)
session.commit()
# Midwest Region
Midwest = Region(name = "Midwest", image_region = "midwest.jpg")
session.add(Midwest)
session.commit()
# North Region
North = Region(name = "North", image_region = "north.jpg")
session.add(North)
session.commit()
# South Region
South = Region(name = "South", image_region = "south.jpg")
session.add(South)
session.commit()
# Williams
college1 = College(user_id=1, name = "Williams College", image_filename = "williams_college.jpg", location = "880 Main St. Williamstown, MA 01267", phone_number = "(413) 597-3131", college_type = "Liberal Arts College", notes = "Your thoughts here", college_region = North)
session.add(college1)
session.commit()
# USC
college2 = College(user_id=1, name = "University of Southern California", image_filename = "usc_college.jpg", college_region = West, location = "Los Angeles, CA 90007", phone_number = "(213) 740-2311", college_type = "Private University", notes = "Your thoughts here")
session.add(college2)
session.commit()
# UNI OF IOWA
college3 = College(user_id=1, name = "University of Iowa", image_filename = "uni_iowa.jpg", college_region = Midwest, location = "Iowa City, IA 52242", phone_number = "(319) 335-3500", college_type = "Public Research University", notes = "Your thoughts here")
session.add(college3)
session.commit()
# UNI OF MONTANA
college4 = College(user_id=1, name = "University of Montana", image_filename = "uni_montana.jpg", college_region = West, location = "32 Campus Dr. Missoula, MT 59812", phone_number = "(406) 243-0211", college_type = "Public Research University", notes = "Your thoughts here")
session.add(college4)
session.commit()
# HIGH PT University
college5 = College(user_id=1, name = "High Point University", image_filename = "highpt_uni.jpg", college_region = South, location = "One University Parkway High Point, NC 27268", phone_number = "(800) 345-6993", college_type = "Private Institution", notes = "Your thoughts here")
session.add(college5)
session.commit()

college6 = College(user_id=1, name = "University of the Ozarks", image_filename = "uni_ozarks.jpg", college_region = South, location = "415 N. College Avenue, Clarksville, AR 72830", phone_number = "(479) 979-1000", college_type = "Private Institution", notes = "Your thoughts here")
session.add(college6)
session.commit()

college7 = College(user_id=1, name = "Cooper Union", image_filename = "cooper_union.jpg", college_region = North, location = "30 Cooper Square, New York, NY 10003", phone_number = "(212) 353-4100", college_type = "Private Institution", notes = "Your thoughts here")
session.add(college7)
session.commit()

college8 = College(user_id=1, name = "Calvin College", image_filename = "calvin_college.jpg", college_region = Midwest, location = "3201 Burton Street SE, Grand Rapids, MI 49546", phone_number = "(800) 688-0122", college_type = "Private Institution", notes = "Your thoughts here")
session.add(college8)
session.commit()
