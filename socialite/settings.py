"""Default socialite settings"""


DSN = 'postgres://socialite:socialite@localhost:5432/socialite'

SECRET = 'super-secret-token-that-must-not-be-used-in-production'

TOKEN_MAX_AGE = 30 * 3600 * 24  # 30 days
