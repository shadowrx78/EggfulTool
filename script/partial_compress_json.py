import json
import sys
import re

def match_path(current_path, target_patterns):
    for pattern in target_patterns:
        regex = "^" + pattern.replace(".", r"\.").replace("[", r"\[").replace("]", r"\]").replace("*", r".*") + "$"
        if re.fullmatch(regex, current_path):
            return True
    return False

def custom_dumps(obj, path="", compress_paths=None, indent=2, level=0, force_compress=False):
    compress_paths = compress_paths or []
    spaces = " " * (level * indent)

    # 如果强制压缩（用于子元素），直接紧凑输出
    if force_compress:
        return json.dumps(obj, separators=(',', ':'), ensure_ascii=False)

    # 检查当前路径是否需要“子项压缩”模式
    should_compress_children = match_path(path, compress_paths)

    if isinstance(obj, dict):
        if not obj:
            return "{}"
        
        if should_compress_children:
            # 外层美化，但每个 value 压缩
            items = []
            for k, v in obj.items():
                key_str = json.dumps(k, ensure_ascii=False)
                child_path = f"{path}.{k}" if path else k
                # 强制压缩这个 value
                val_str = custom_dumps(v, child_path, compress_paths, indent, level + 1, force_compress=True)
                items.append(f"{key_str}: {val_str}")
            inner = ("," + "\n" + spaces + "  ").join(items)
            return "{\n" + spaces + "  " + inner + "\n" + spaces + "}"
        else:
            # 默认递归美化
            items = []
            for k, v in obj.items():
                key_str = json.dumps(k, ensure_ascii=False)
                child_path = f"{path}.{k}" if path else k
                val_str = custom_dumps(v, child_path, compress_paths, indent, level + 1)
                items.append(f"{key_str}: {val_str}")
            inner = ("," + "\n" + spaces + "  ").join(items)
            return "{\n" + spaces + "  " + inner + "\n" + spaces + "}"

    elif isinstance(obj, list):
        if not obj:
            return "[]"
        
        if should_compress_children:
            # 外层美化，但每个元素压缩
            items = []
            for i, v in enumerate(obj):
                child_path = f"{path}[{i}]"
                item_str = custom_dumps(v, child_path, compress_paths, indent, level + 1, force_compress=True)
                items.append(item_str)
            inner = ("," + "\n" + spaces + "  ").join(items)
            return "[\n" + spaces + "  " + inner + "\n" + spaces + "]"
        else:
            # 默认递归美化
            items = []
            for i, v in enumerate(obj):
                child_path = f"{path}[{i}]"
                item_str = custom_dumps(v, child_path, compress_paths, indent, level + 1)
                items.append(item_str)
            inner = ("," + "\n" + spaces + "  ").join(items)
            return "[\n" + spaces + "  " + inner + "\n" + spaces + "]"

    else:
        return json.dumps(obj, ensure_ascii=False)

def main(input_file, output_file=None, compress_keys=None):
    compress_keys = compress_keys or []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 读取 JSON 失败: {e}", file=sys.stderr)
        return

    try:
        result = custom_dumps(data, "", compress_keys, indent=2)
    except Exception as e:
        print(f"❌ 序列化失败: {e}", file=sys.stderr)
        return

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"✅ 输出到: {output_file}")
    else:
        print(result)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python partial_compress_json.py <input.json> [output.json] [--compress key1 key2 ...]")
        print("示例: python partial_compress_json.py data.json out.json --compress items.effect dataInfo")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = None
    compress_list = []

    if "--compress" in sys.argv:
        idx = sys.argv.index("--compress")
        compress_list = sys.argv[idx + 1:]
        if len(sys.argv) > 2 and sys.argv[2] != "--compress":
            output_path = sys.argv[2]
    else:
        output_path = sys.argv[2] if len(sys.argv) > 2 else None

    main(input_path, output_path, compress_list)