# Debug mode gives nicer error messages and enables serving of static media
# directly from the Python process.  It is highly insecure, however, so be sure
# to turn it off before going to production.
DEBUG = False

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ykzp27^ltn1ump9lrtim@*u#9k=8k#l0wpzy-k^e(yu)+zpy8a'

# This tells all of the Clutch systems how to talk to your PostgreSQL database,
# so if you are running it on a different host, you should change the host and
# port information here (as well as any security credentials your setup
# requires.)
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
}

# Enter your Amazon Web Services S3 access key, secret, and the bucket name.
# (This is necessary for hybrid native/html application framework ONLY.)
AWS_ACCESS_KEY = ''
AWS_ACCESS_SECRET = ''
AWS_BUCKET_NAME = ''

# The host and port that the Clutch RPC server should run on.
CLUTCH_RPC_HOST = '0.0.0.0'
CLUTCH_RPC_PORT = 41674

# This is the URL that the tunnel should use to communicate with the Clutch
# RPC server. This may differ from the CLUTCH_RPC_HOST and the CLUTCH_RPC_PORT
# if the RPC server is running on a different servers.
CLUTCH_RPC_URL = 'http://127.0.0.1:41674/'

# The host and port that the Clutch Tunnel server should run on.
CLUTCH_TUNNEL_HOST = '127.0.0.1'
CLUTCH_TUNNEL_PORT = 41675
