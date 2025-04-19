import os
import re
import pandas as pd
import tiktoken

from graphrag.config.enums import ModelType
from graphrag.config.models.language_model_config import LanguageModelConfig
from graphrag.language_model.manager import ModelManager
from graphrag.query.indexer_adapters import (
    read_indexer_communities,
    read_indexer_entities,
    read_indexer_reports,
)
from .custom.custom_global_search import GlobalSearchCustom
from graphrag.query.structured_search.global_search.community_context import (
    GlobalCommunityContext,
)
from graphrag.query.structured_search.global_search.search import GlobalSearch
from .custom.custom_prompt import GLOBAL_SEARCH_MAP_SYSTEM_PROMPT, GLOBAL_SEARCH_REDUCE_SYSTEM_PROMPT,GLOBAL_SEARCH_KNOWLEDGE_SYSTEM_PROMPT
from ..constants.constants import (
    INPUT_DIR,
    LANCEDB_URI,
    COMMUNITY_REPORT_TABLE,
    ENTITY_TABLE,
    COMMUNITY_TABLE,
    RELATIONSHIP_TABLE,
    COVARIATE_TABLE,
    TEXT_UNIT_TABLE,
    COMMUNITY_LEVEL,
)
from dotenv import load_dotenv
load_dotenv()
class GraphragGlobalSearch:
    def __init__(self):
        self.api_key = os.environ.get("GRAPHRAG_API_KEY")
        self.llm_model = os.environ.get("GRAPHRAG_LLM_MODEL")
        self.input_dir = INPUT_DIR
        self.lancedb_uri = LANCEDB_URI
        self.community_report_table = COMMUNITY_REPORT_TABLE    
        self.entity_table = ENTITY_TABLE
        self.community_table = COMMUNITY_TABLE
        self.relationship_table = RELATIONSHIP_TABLE
        self.covariate_table = COVARIATE_TABLE
        self.text_unit_table = TEXT_UNIT_TABLE
        self.community_level = COMMUNITY_LEVEL
        self.config = LanguageModelConfig(
            api_key=self.api_key,
            type=ModelType.OpenAIChat,
            model=self.llm_model,
            max_retries=20,
        )
        self.model = ModelManager().get_or_create_chat_model(
            name="global_search",
            model_type=ModelType.OpenAIChat,
            config=self.config,
        )
        self.token_encoder = tiktoken.encoding_for_model(self.llm_model)
        self.community_df= pd.read_parquet(f"{self.input_dir}/{self.community_table}.parquet")
        self.entity_df= pd.read_parquet(f"{self.input_dir}/{self.entity_table}.parquet")
        self.report_df= pd.read_parquet(f"{self.input_dir}/{self.community_report_table}.parquet")
        self.communities = read_indexer_communities(self.community_df, self.report_df)
        self.reports = read_indexer_reports(self.report_df, self.community_df, self.community_level)
        self.entities = read_indexer_entities(self.entity_df, self.community_df, self.community_level)
        self.context_builder = GlobalCommunityContext(
            community_reports=self.reports,
            communities=self.communities,
            entities=self.entities,  # default to None if you don't want to use community weights for ranking
            token_encoder=self.token_encoder,
        )
        self.context_builder_params = {
            "use_community_summary": False,  # False means using full community reports. True means using community short summaries.
            "shuffle_data": True,
            "include_community_rank": True,
            "min_community_rank": 0,
            "community_rank_name": "rank",
            "include_community_weight": True,
            "community_weight_name": "occurrence weight",
            "normalize_community_weight": True,
            "max_tokens": 12_000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 5000)
            "context_name": "Reports",
        }

        self.map_llm_params = {
            "max_tokens": 1000,
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }

        self.reduce_llm_params = {
            "max_tokens": 2000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 1000-1500)
            "temperature": 0.0,
        }
        self.search_engine = GlobalSearch(
            model=self.model,
            context_builder=self.context_builder,
            token_encoder=self.token_encoder,
            max_data_tokens=12_000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 5000)
            map_llm_params=self.map_llm_params,
            reduce_llm_params=self.reduce_llm_params,
            allow_general_knowledge=False,  # set this to True will add instruction to encourage the LLM to incorporate general knowledge in the response, which may increase hallucinations, but could be useful in some use cases.
            json_mode=True,  # set this to False if your LLM model does not support JSON mode.
            context_builder_params=self.context_builder_params,
            concurrent_coroutines=32,
            response_type="multiple paragraphs",  # free form text describing the response type and format, can be anything, e.g. prioritized list, single paragraph, multiple paragraphs, multiple-page report
        )
        self.search_engine_custom = GlobalSearchCustom(
            model=self.model,
            context_builder=self.context_builder,
            map_system_prompt=GLOBAL_SEARCH_MAP_SYSTEM_PROMPT,
            reduce_system_prompt=GLOBAL_SEARCH_REDUCE_SYSTEM_PROMPT,
            token_encoder=self.token_encoder,
            max_data_tokens=12_000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 5000)
            map_llm_params=self.map_llm_params,
            reduce_llm_params=self.reduce_llm_params,
            allow_general_knowledge=False,  # set this to True will add instruction to encourage the LLM to incorporate general knowledge in the response, which may increase hallucinations, but could be useful in some use cases.
            json_mode=True,  # set this to False if your LLM model does not support JSON mode.
            context_builder_params=self.context_builder_params,
            concurrent_coroutines=32,
            general_knowledge_inclusion_prompt=GLOBAL_SEARCH_KNOWLEDGE_SYSTEM_PROMPT,
        )
    async def global_search(self, prompt):
        response = await self.search_engine.search(prompt)
        return re.sub(r"\[Data:.*?\]", "", response.response), []
    async def global_search_custom(self, prompt):
        response = await self.search_engine_custom.search(prompt)
        return re.sub(r"\[Data:.*?\]", "", response.response), []