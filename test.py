from langchain.chat_models import ChatOpenAI
from langchain.chains import create_extraction_chain
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter

# Schema
schema = {
    "properties": {
        "甲方": {"type": "string"},
    },
    "required": ["甲方"],
}

# Input 
# inp = """Alex is 5 feet tall. Claudia is 1 feet taller Alex and jumps higher than him. Claudia is a brunette and Alex is blonde."""

loader = PyPDFLoader('docs/lianjia.pdf')
text_splitter = CharacterTextSplitter(        
    separator = "\n\n",
    chunk_size = 5000,
    chunk_overlap  = 200,
    length_function = len,
    is_separator_regex = False,
)
pages = loader.load_and_split(text_splitter)
print(pages[3])

# Run chain
# llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
# chain = create_extraction_chain(schema, llm)
# chain.run(inp)