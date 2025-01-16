import asyncio
from abc import abstractmethod
from json import JSONDecodeError

from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.outputs import Generation
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables.utils import Input
from loguru import logger

from kvidgen.core.agents.base_model import GPT4o
from kvidgen.core.agents.prompts import (
    EDIT_SYSTEM_PROMPT,
    EDIT_USER_PROMPT,
    IMAGE_EFFECTS_SYSTEM_PROMPT,
)


class AgentABC:
    def __init__(self):
        self.llm: GPT4o = GPT4o()

    @abstractmethod
    async def run(self, ipt: Input):
        pass


class Editor(AgentABC):
    def __init__(self):
        super().__init__()
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


class ImageEffectsOutputParser(JsonOutputParser):
    def parse_result(self, result: list[Generation], *, partial: bool = False) -> list:

        try:
            rst = super().parse_result(result)
            effects = rst.get("effects", ["zoom"])
            return effects

        except JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}")
            return ["zoom"]


class ImageEffectsArtist(AgentABC):
    def __init__(self):
        super().__init__()
        self.system_prompt = IMAGE_EFFECTS_SYSTEM_PROMPT
        self.output_parser = ImageEffectsOutputParser()

    async def run(self, ipt: Input):
        result = (
            await (self.llm | self.output_parser).ainvoke(
                [
                    SystemMessage(content=self.system_prompt),
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpg;base64, {ipt}"},
                            },
                        ],
                    },
                ]
            ),
        )
        logger.debug(f"Generated image effects: {result}")
        return result


async def main():
    result = await ImageEffectsArtist().run(
        "https://thumb.qsmutual.com/data/zyc/2025/01/07/a0ef20f6-4046-42fa-a296-ae1c76b45c56.jpg@!love.png"
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
