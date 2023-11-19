from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter

load_dotenv()

schema = {
    "properties": {
        "name": {"type": "string"},
        "height": {"type": "integer"},
        "hair_color": {"type": "string"},
    },
    "required": ["name", "height"],
}

contract_schema = {
    "properties": {
      "房屋出租方姓名": {"type": "string"},
      "房屋出租方性别": {"type": "string"},
      "房屋出租方身份证号码": {"type": "string"},
      "房屋承租方姓名": {"type": "string"},
      "房屋承租方性别": {"type": "string"},
      "房屋承租方身份证号码": {"type": "string"},
      "出租房屋坐落地址": {"type": "string"},
      "原合同编号": {"type": "string"},
      "本合同编号": {"type": "string"},
      "建筑面积": {"type": "string"},
      "每月租金": {"type": "string"},
    },
    "required": ["房屋出租方", "房屋承租方"],
}

# Run 
# query = """Alex is 5 feet tall. Claudia is 1 feet taller Alex and jumps higher than him. Claudia is a brunette and Alex is blonde."""
# inp = """老王身高5英尺。Claudia 比 老王高1英尺，并且比他跳得更高。Claudia 是棕发，而 老王是金发。
# 老李身高有6英尺，当然由于是中国人，所以头发是黑色的。"""

inp = """
    交易方留存信息表\n交易方留存信息表\n房屋出租方\n\t\n甲方（签章）：\n甲方（签章）：\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t\t\t\n年\n年\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\n月\n月\n\t\t\t\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t\t\t\t\n日\n日\n姓名\n周树凤\n英文名\nX\n性别\n女\n国籍\n中国\n出生日期\n1962\n年\n11\n月\n26\n日\n证件名称\n身份证\n证件号码\n110108196211262262\n电子邮箱\nX\n通讯地址\n北京市海淀区学院路37号411宅309号\n21.0
    """
loader = PyPDFLoader('docs/lianjia.pdf')
text_splitter = CharacterTextSplitter(
    chunk_size = 5000,
    chunk_overlap  = 200,
    length_function = len,
    is_separator_regex = False,
)
pages = loader.load_and_split(text_splitter)
text = '\n'.join([page.page_content for page in pages])

print(text)
# Run chain
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))
chain = create_extraction_chain(contract_schema, llm)
output = chain.run(text.replace('\n', '\\n').replace('\t', '\\t'))
print(output)
