from main.settings import BASE_DIR
BOT = "5998285338:AAH0Sc3S_nfMO1Ow3zeP23IHT82kNy34quE"
DATABASE = BASE_DIR/"db.sqlite3"


full_path = BASE_DIR.joinpath('cdn', 'media', '')

# Convert to string representation
full_path_str = str(full_path)

# Replace backslashes with forward slashes
full_path_str = full_path_str.replace("\\", "/")

# Append a forward slash after '/cdn/media'
full_path_str += '/'
IMAGE = full_path_str
print("Full path:", full_path_str)
# IMAGE = base_path / 'cdn' / 'media'