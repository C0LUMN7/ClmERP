# -*- coding: utf-8 -*-
"""YAML 用例加载与运行上下文

职责：
- load_case_pairs(): 加载接口用例 YAML，按文件顺序展开为 (base_info, testcase) 对
- RunContext: 每次测试会话独立的运行上下文，保存接口间传递的提取变量，
  替代旧全局 extract.yaml，避免并发和失败重跑时相互污染
"""
import yaml


def load_case_pairs(yaml_file):
    """加载接口用例 YAML 文件，返回 [(base_info, testcase), ...]

    兼容两种现有格式：
    - 单接口文件：一个或多个 baseInfo 块，每块一个或多个 testCase
    - 业务场景文件：多个 baseInfo 块顺序排列，每块一个 testCase
    两种格式都按文件顺序展开为 (base_info, testcase) 对。
    """
    with open(yaml_file, 'r', encoding='utf-8') as f:
        blocks = yaml.safe_load(f) or []
    pairs = []
    for block in blocks:
        base_info = block.get('baseInfo')
        for testcase in block.get('testCase', []):
            pairs.append((base_info, testcase))
    return pairs


class RunContext:
    """每次测试会话独立的运行上下文，保存接口间传递的提取变量"""

    def __init__(self):
        self._vars = {}

    def set(self, name, value):
        self._vars[name] = value

    def get(self, name, default=None):
        return self._vars.get(name, default)

    def update(self, values):
        self._vars.update(values)

    def clear(self):
        self._vars.clear()

    def __contains__(self, name):
        return name in self._vars

    def names(self):
        return list(self._vars.keys())


_context = None


def get_run_context():
    """获取当前测试会话的运行上下文（会话内单例）"""
    global _context
    if _context is None:
        _context = RunContext()
    return _context


def reset_run_context():
    """开始新测试会话时重置运行上下文，返回新上下文"""
    global _context
    _context = RunContext()
    return _context
