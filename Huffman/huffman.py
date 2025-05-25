
from collections import defaultdict,deque
import heapq

class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq


def build_frequency_table(data: bytes) -> dict:
    frequency = defaultdict(int)
    for byte in data:
        frequency[byte] += 1
    return frequency


def build_huffman_tree(frequency: dict) -> HuffmanNode:
    heap = []
    for char, freq in frequency.items():
        heapq.heappush(heap, HuffmanNode(char=char, freq=freq))
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)
    
    return heapq.heappop(heap)


def build_codes(root: HuffmanNode, current_code: str = "", codes: dict = None) -> dict:
    if codes is None:
        codes = {}
    
    if root is None:
        return codes
    
    if root.char is not None:
        codes[root.char] = current_code
        return codes
    
    build_codes(root.left, current_code + "0", codes)
    build_codes(root.right, current_code + "1", codes)
    
    return codes


def serialize_tree(root: HuffmanNode) -> str:
    """Serialize Huffman tree using pre-order traversal with special markers"""
    if root is None:
        return ""
    
    if root.char is not None:
        return f"1{chr(root.char)}"
    
    return f"0{serialize_tree(root.left)}{serialize_tree(root.right)}"


def deserialize_tree(data: deque) -> HuffmanNode:
    """Deserialize Huffman tree from serialized string"""
    if not data:
        return None
    
    bit = data.popleft()
    if bit == '1':
        char = ord(data.popleft())
        return HuffmanNode(char=char)
    else:
        left = deserialize_tree(data)
        right = deserialize_tree(data)
        return HuffmanNode(left=left, right=right)
