from pathlib import Path
from src.configs.common_configs import PathConfig

class RFC:
    def __init__(self) -> None:
        self.rfc_path = PathConfig().rfc
        # 存储rfc文件的列表
        self.file_list = []
        # 遍历rfc文件夹下的所有文件
        for file in self.rfc_path.iterdir():
            self.file_list.append(file.name)
    
    def rfc_existed(self, file: str) -> bool:
        # file_name = f"RFC{file}.txt"
        # print(f"Existed: {file}")
        # 判断文件是否存在
        if file in self.file_list:
            return True
        return False
    
    def file_path(self, file: str) -> Path:
        file_name = f"RFC{file}.txt"
        assert self.rfc_existed(file_name), f"RFC{file} is not existed"
        return self.rfc_path / file_name
