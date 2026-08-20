# -*- coding: utf-8 -*-
"""旧 extract.yaml 读取兼容。"""
from pathlib import Path

import yaml

from shared.logger import logs

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EXTRACT_FILE = _REPO_ROOT / 'extract.yaml'


class LegacyYamlStore:
    """只读兼容旧 extract.yaml 中的接口提取变量。"""

    def __init__(self, extract_file=None):
        self.extract_file = Path(extract_file) if extract_file else _EXTRACT_FILE

    def read_all(self):
        if not self.extract_file.exists():
            logs.error('extract.yaml不存在')
            return {}
        try:
            with self.extract_file.open('r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except Exception as e:
            logs.error(f'读取旧 extract.yaml 失败: {e}')
            return {}

    def get_extract_yaml(self, node_name, second_node_name=None):
        data = self.read_all()
        try:
            if second_node_name is None:
                return data[node_name]
            return data[node_name][second_node_name]
        except Exception as e:
            logs.error(f"【extract.yaml】没有找到：{node_name},--{e}")
            return None


def get_extract_yaml(node_name, second_node_name=None):
    return LegacyYamlStore().get_extract_yaml(node_name, second_node_name)
