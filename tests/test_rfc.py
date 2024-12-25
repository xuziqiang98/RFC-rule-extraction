import path_setup
from src.rfc import RFC

rfc = RFC()
file = '4271'
print(f"RFC Folder Path: {rfc.rfc_path}")
print(f"All RFC files: {rfc.file_list}")
# print(f"Specific file is existed: {rfc.rfc_existed(file)}")
print(f"Specific file path: {rfc.file_path(file)}")