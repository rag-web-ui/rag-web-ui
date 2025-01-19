# 同步算法的实现和验证
# 算法说明：
# 1. 使用哈希表(defaultdict)建立content_hash到chunks的映射，时间复杂度O(n)
# 2. 使用集合操作找到相同位置的chunks，时间复杂度O(n)
# 3. 使用双指针法进行剩余chunks的匹配，时间复杂度O(n)
# 总体时间复杂度: O(n)，其中n为chunks的总数
# 空间复杂度: O(n)，主要用于存储哈希表

from collections import defaultdict
from typing import TypedDict, List, Dict, Set
from dataclasses import dataclass

@dataclass
class Chunk:
    index: int
    content_hash: str
    chunk_content: str
    uuid: str = None

class SyncResult(TypedDict):
    to_create: List[Dict]
    to_update: List[Dict]
    to_delete: List[str]

# 模拟后端的旧 chunks 数据
old_chunks = [
    {'uuid': 'uuid_1', 'index': 0, 'content_hash': 'hash_A', 'chunk_content': '这是第一段。'},
    {'uuid': 'uuid_2', 'index': 1, 'content_hash': 'hash_B', 'chunk_content': '这是第二段。'},
    {'uuid': 'uuid_3', 'index': 2, 'content_hash': 'hash_C', 'chunk_content': '这是第三段。'},
    {'uuid': 'uuid_4', 'index': 3, 'content_hash': 'hash_D', 'chunk_content': '这是第四段。'},
    {'uuid': 'uuid_5', 'index': 4, 'content_hash': 'hash_E', 'chunk_content': '这是第五段。'},
]

# 模拟 GitHub Actions 生成的新 chunks 数据
new_chunks = [
    {'index': 0, 'content_hash': 'hash_A', 'chunk_content': '这是第一段。'},
    {'index': 1, 'content_hash': 'hash_C', 'chunk_content': '这是第三段。'},
    {'index': 2, 'content_hash': 'hash_D', 'chunk_content': '这是第四段。'},
    {'index': 3, 'content_hash': 'hash_D', 'chunk_content': '这是第四段。'},
    {'index': 4, 'content_hash': 'hash_D', 'chunk_content': '这是第四段。'},
    {'index': 5, 'content_hash': 'hash_D', 'chunk_content': '这是第四段。'},
    {'index': 6, 'content_hash': 'hash_D', 'chunk_content': '这是第四段。'},
]

def synchronize_chunks(old_chunks: List[Dict], new_chunks: List[Dict]) -> SyncResult:
    """
    基于 content_hash + index 的双指针匹配算法，查找需要新增、更新和删除的 chunks。
    主要改进：
    1. 对同一 content_hash 的旧、新 chunks，分别按 index 排序，再逐个匹配，避免原先直接根据
       “两两相同位置”导致重复 content_hash 时的混淆。
    2. 保留了原先的距离阈值(distance <= threshold)判断，但逻辑更直观，减少漏匹或误判。
    """

    # ========== 1. 输入验证 ==========
    if not isinstance(old_chunks, list) or not isinstance(new_chunks, list):
        raise TypeError("输入参数必须是列表类型")

    required_fields = {'index', 'content_hash', 'chunk_content'}
    for chunk in old_chunks:
        if not required_fields.union({'uuid'}).issubset(chunk.keys()):
            raise ValueError("旧chunks缺少必要字段")
    for chunk in new_chunks:
        if not required_fields.issubset(chunk.keys()):
            raise ValueError("新chunks缺少必要字段")

    # ========== 2. 构建 content_hash => chunks 的映射表，减少跨 content_hash 的错误匹配 ==========
    old_chunks_by_hash = defaultdict(list)
    for oc in old_chunks:
        old_chunks_by_hash[oc['content_hash']].append(oc)

    new_chunks_by_hash = defaultdict(list)
    for nc in new_chunks:
        new_chunks_by_hash[nc['content_hash']].append(nc)

    # ========== 3. 遍历所有的 content_hash，逐个匹配 ==========

    to_create = []
    to_update = []
    to_delete = []

    # “并”集获取所有出现过的 content_hash
    all_hashes = set(old_chunks_by_hash.keys()) | set(new_chunks_by_hash.keys())

    # 允许的更新距离阈值，可根据需要调大或调小
    threshold = 10

    for content_hash in all_hashes:
        old_list = sorted(old_chunks_by_hash[content_hash], key=lambda x: x['index'])
        new_list = sorted(new_chunks_by_hash[content_hash], key=lambda x: x['index'])

        i, j = 0, 0
        len_old, len_new = len(old_list), len(new_list)

        while i < len_old and j < len_new:
            old_entry = old_list[i]
            new_entry = new_list[j]
            distance = abs(old_entry['index'] - new_entry['index'])

            # 如果索引相近，则判定为同一块内容，执行更新操作
            if distance <= threshold:
                to_update.append({
                    'uuid': old_entry['uuid'],
                    'index': new_entry['index'],
                    'content_hash': content_hash,
                    'chunk_content': new_entry['chunk_content']
                })
                i += 1
                j += 1

            # 如果旧 chunk.index 更小，说明它在新列表里没有合适的配对，需要删除
            elif old_entry['index'] < new_entry['index']:
                to_delete.append(old_entry['uuid'])
                i += 1

            # 否则，新 chunk.index 更小，说明这是新增加的块
            else:
                to_create.append({
                    'index': new_entry['index'],
                    'content_hash': content_hash,
                    'chunk_content': new_entry['chunk_content']
                })
                j += 1

        # 把剩余的旧 chunks 视为需要删除
        while i < len_old:
            to_delete.append(old_list[i]['uuid'])
            i += 1

        # 把剩余的新 chunks 视为需要新增
        while j < len_new:
            to_create.append({
                'index': new_list[j]['index'],
                'content_hash': content_hash,
                'chunk_content': new_list[j]['chunk_content']
            })
            j += 1

    return {
        'to_create': to_create,
        'to_update': to_update,
        'to_delete': to_delete
    }

if __name__ == '__main__':
    result = synchronize_chunks(old_chunks, new_chunks)

    print("需要创建的 chunks:")
    if result['to_create']:
        for chunk in result['to_create']:
            print(chunk)
    else:
        print("null")

    print("\n需要更新的 chunks:")
    if result['to_update']:
        for chunk in result['to_update']:
            print(chunk)
    else:
        print("null")

    print("\n需要删除的 chunks:")
    if result['to_delete']:
        for uuid in result['to_delete']:
            print(uuid)
    else:
        print("null")