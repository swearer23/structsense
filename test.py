import json

def extract_json_from_text(text):
    try:
        # 尝试解析输入文本中的JSON
        json_data = json.loads(text)
        return json_data
    except json.JSONDecodeError:
        # 如果无法解析为JSON，则返回None
        return None

# 示例用法
input_text = 'Some text before JSON: {"key": "value"} Some text after JSON.'
json_result = extract_json_from_text(input_text)

if json_result is not None:
    print("Parsed JSON content:")
    print(json.dumps(json_result, indent=4))
else:
    print("No JSON content found.")