# from langchain import OpenAI
# from langchain.chat_models import ChatOpenAI
# from langchain.document_loaders import TextLoader
# from langchain.llms import TextGen
# from langchain.chains import create_extraction_chain

# model_url = "http://localhost:5000"
# # Loaders

# with open('docs/BYD_Annual_Report.txt', 'r') as f:
#     text_data = f.read()

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
# texts = text_splitter.create_documents([text_data])

# llm = TextGen(model_url=model_url, temperature=0.1)

# # schema = {
# #     "properties": {
# #         "研发投入": {"type": "string"},
# #     },
# #     "required": [],
# # }

# # Schema
# schema = {
#     "properties": {
#         "name": {"type": "string"},
#         "height": {"type": "integer"},
#         "hair_color": {"type": "string"},
#     },
#     "required": ["name", "height"],
# }

# # Input 
# inp = """Alex is 5 feet tall. Claudia is 1 feet taller Alex and jumps higher than him. Claudia is a brunette and Alex is blonde."""


# # Run chain
# chain = create_extraction_chain(schema, llm)
# chain.run(inp)
import json
from langchain.llms import TextGen
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import (
    PromptTemplate,
)

model_url = "http://0.0.0.0:5000"

loader = PyPDFLoader('docs/lianjia.pdf')
text_splitter = CharacterTextSplitter(
    chunk_size = 5000,
    chunk_overlap  = 200,
    length_function = len,
    is_separator_regex = False,
)
pages = loader.load_and_split(text_splitter)
        
llm = TextGen(model_url=model_url, temperature=0.001, top_p=0.95, top_k=1, max_tokens=5000)

# chain = create_extraction_chain(schema, llm)

extract_schema = {
  "renter": "房屋出租方姓名",
  "rentee": "房屋承租方姓名",
}

extract_template = json.dumps(extract_schema)
example_response = json.dumps({"renter": "张三"})

prompt = PromptTemplate(
    template="""
Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.
### Instruction:
从以下Input部分的内容中抽取以下信息：
```
{extract_template}
```
response部分中应仅包含抽取信息的json格式，不要添加任何评论

### Input:
{query}

### Response:

    """,
    input_variables=["query", "extract_template"]
)

inp = prompt.format_prompt(query=pages[1].page_content.replace('\n', '\\n').replace('\t', '\\t'), extract_template=extract_template)
output = llm(inp.to_string(),)
print(output)

# for page in pages:
    
#     _input = prompt.format_prompt(query=page)
#     output = llm(_input.to_string())
#     print(output)


# # Set up a parser + inject instructions into the prompt template.
# parser = PydanticOutputParser(pydantic_object=People)

# # Prompt
# prompt = PromptTemplate(
#     template="""
# Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.
# ### Instruction:
# Answer the user query.\n{format_instructions}\n
# ### Input:
# {query}\n
# ### Response:
#     """,
#     input_variables=["query"],
#     partial_variables={"format_instructions": parser.get_format_instructions()},
# )

# # Run
# _input = prompt.format_prompt(query=query)
# # model = OpenAI(temperature=0)
# llm = TextGen(model_url=model_url, temperature=0.1)
# output = llm(_input.to_string())

# print('==================', output)
# parser.parse(output)
