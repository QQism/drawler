import dj_database_url

DEBUG = True

# Replace with the appropriate database url OR set DATABASE_ENV
#DATABASES = {
#    'default': dj_database_url.config(
#        default='postgres://postgres:postgres@localhost:5432/tiengviet')
#}
DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Ho_Chi_Minh'
