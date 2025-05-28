from utils.db_init import init_tables
from utils.config import get_display_currency
currency = get_display_currency()

init_tables()
print("All required tables have been created or verified.")

