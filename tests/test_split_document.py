import path_setup
from src.utils import split_document_by_sections
from src.rfc import RFC

rfc = '2328'
# rfc = '4271'
# rfc_path = RFC().file_path(rfc)
# print(f"RFC Folder Path: {rfc_path}")
sections = split_document_by_sections(rfc)
print(f"一共有{len(sections)}个section")
for k, v in sections.items():
    print(f"Section {k}")