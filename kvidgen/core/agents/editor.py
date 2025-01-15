from abc import abstractmethod

from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables.utils import Input

from kvidgen.core.agents.base_model import GPT4o
from kvidgen.core.agents.prompts import EDIT_SYSTEM_PROMPT, EDIT_USER_PROMPT


class AgentABC:
    @abstractmethod
    async def run(self, ipt: Input):
        pass


class Editor(AgentABC):
    def __init__(self):
        self.llm: GPT4o = GPT4o()
        self.system_prompt = EDIT_SYSTEM_PROMPT
        self.user_prompt = EDIT_USER_PROMPT
        self.output_parser = StrOutputParser()

    async def run(self, ipt):
        return await (
            ChatPromptTemplate.from_messages(
                [
                    SystemMessage(content=self.system_prompt),
                    HumanMessagePromptTemplate.from_template(self.user_prompt),
                ]
            )
            | self.llm
            | self.output_parser
        ).ainvoke(ipt)
