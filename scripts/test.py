from typing import Optional, List
from pydantic import BaseModel, Field
from langchain.chains import create_extraction_chain_pydantic
from langchain.llms import TextGen
from typing import Sequence
from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.output_parsers import PydanticOutputParser

# Pydantic data class
class Person(BaseModel):
    person_name: str
    person_height: int
    person_hair_color: str
    dog_breed: Optional[str]
    dog_name: Optional[str]

class People(BaseModel):
    """Identifying information about all people in a text."""
    people: Sequence[Person]

model_url = "http://localhost:5000/v1/completions"
llm = TextGen(model_url=model_url, temperature=0.001, top_p=0.95, top_k=1, max_tokens=5000) 

# Set up a parser + inject instructions into the prompt template.
parser = PydanticOutputParser(pydantic_object=People)

query = """Alex is 5 feet tall. Claudia is 1 feet taller Alex and jumps higher than him. Claudia is a brunette and Alex is blonde."""
# Prompt
prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Run
_input = prompt.format_prompt(query=query)
print(_input.text)
output = llm(_input.to_string())
parser.parse(output)