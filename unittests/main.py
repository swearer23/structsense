import os
import sys

# 获取当前文件的路径（即 test_main.py 所在目录）
current_dir = os.path.dirname(__file__)

# 将项目根目录添加到 Python 解释器的搜索路径中
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(root_dir)

from app import app
import pytest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_upload_file(client):
    # 构造一个测试用的文件
    file_data = {
        'file': open(os.path.join(root_dir, './docs/PO.PDF'), 'rb'),
        'templateName': 'WoolWorthsGroupPOContract'
    }

    # 发送 POST 请求到接口
    response = client.post('/uploadPOFile',
      data=file_data,
      content_type='multipart/form-data'
    )
    # 检查是否收到了正确的响应
    assert response.status_code == 200
    data = response.get_json()
    assert data.get('po_main').get('ccusperson').get('value') == 'Nick Allan'
