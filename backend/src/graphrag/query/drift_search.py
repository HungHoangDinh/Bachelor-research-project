import os
from pathlib import Path

import pandas as pd
import tiktoken
import re
from graphrag.config.enums import ModelType
from graphrag.config.models.drift_search_config import DRIFTSearchConfig
from graphrag.config.models.language_model_config import LanguageModelConfig
from graphrag.language_model.manager import ModelManager
from .custom.custom_drift_search import DRIFTSearchCustom
from graphrag.query.indexer_adapters import (
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_report_embeddings,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.structured_search.drift_search.drift_context import (
    DRIFTSearchContextBuilder,
)
from graphrag.query.structured_search.drift_search.search import DRIFTSearch
from graphrag.vector_stores.lancedb import LanceDBVectorStore
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
from .custom.custom_prompt import DRIFT_SEARCH_REDUCE_PROMPT, DRIFT_SEARCH_SYSTEM_PROMPT, LOCAL_SEARCH_SYSTEM_PROMPT
from dotenv import load_dotenv
load_dotenv()
class GraphragDriftSearch:
    def __init__(self):
        self.input_dir = INPUT_DIR
        self.lancedb_uri = LANCEDB_URI
        self.community_report_table = COMMUNITY_REPORT_TABLE
        self.entity_table = ENTITY_TABLE
        self.community_table = COMMUNITY_TABLE
        self.relationship_table = RELATIONSHIP_TABLE
        self.covariate_table = COVARIATE_TABLE
        self.text_unit_table = TEXT_UNIT_TABLE
        self.community_level = COMMUNITY_LEVEL
        self.drift_search_config = DRIFTSearchConfig()
        self.entity_df=pd.read_parquet(f"{self.input_dir}/{self.entity_table}.parquet")
        self.community_df=pd.read_parquet(f"{self.input_dir}/{self.community_table}.parquet")
        self.entities= read_indexer_entities(self.entity_df, self.community_df, self.community_level)
        self.description_embedding_store= self._get_description_embedding_store()
        self.full_content_embedding_store= self._get_full_content_embedding_store()
        self.relationship_df=pd.read_parquet(f"{self.input_dir}/{self.relationship_table}.parquet")
        self.relationships= read_indexer_relationships(self.relationship_df)
        self.text_unit_df=pd.read_parquet(f"{self.input_dir}/{self.text_unit_table}.parquet")
        self.text_units= read_indexer_text_units(self.text_unit_df)
        
        self.api_key = os.environ["GRAPHRAG_API_KEY"]
        self.llm_model = os.environ["GRAPHRAG_LLM_MODEL"]
        self.embedding_model = os.environ["GRAPHRAG_EMBEDDING_MODEL"]
        self.chat_config = LanguageModelConfig(
            api_key=self.api_key,
            type=ModelType.OpenAIChat,
            model=self.llm_model,
            max_retries=20,
        )
        self.chat_model = ModelManager().get_or_create_chat_model(
            name="local_search",
            model_type=ModelType.OpenAIChat,
            config=self.chat_config,
        )
        self.token_encoder = tiktoken.encoding_for_model(self.llm_model)
        self.embedding_config = LanguageModelConfig(
            api_key=self.api_key,
            type=ModelType.OpenAIEmbedding,
            model=self.embedding_model,
            max_retries=20,
        )
        self.text_embedder = ModelManager().get_or_create_embedding_model(
            name="local_search_embedding",
            model_type=ModelType.OpenAIEmbedding,
            config=self.embedding_config,
        )
        self.reports=self._get_reports()
        self.drift_params = DRIFTSearchConfig(
            temperature=0,
            max_tokens=12_000,
            primer_folds=1,
            drift_k_followups=3,
            n_depth=2,
            n=1,
        )
        self.context_builder = DRIFTSearchContextBuilder(
             model=self.chat_model,
            text_embedder=self.text_embedder,
            entities=self.entities,
            relationships=self.relationships,
            reports=self.reports,
            entity_text_embeddings=self.description_embedding_store,
            text_units=self.text_units,
            token_encoder=self.token_encoder,
            config=self.drift_params,
        )
        self.context_builder_custom = DRIFTSearchContextBuilder(
            model=self.chat_model,
            text_embedder=self.text_embedder,
            entities=self.entities,
            relationships=self.relationships,
            reports=self.reports,
            entity_text_embeddings=self.description_embedding_store,
            text_units=self.text_units,
            token_encoder=self.token_encoder,
            config=self.drift_params,
            local_system_prompt= DRIFT_SEARCH_SYSTEM_PROMPT,
            reduce_system_prompt=DRIFT_SEARCH_REDUCE_PROMPT,
        )
        self.search = DRIFTSearch(
            model=self.chat_model, context_builder=self.context_builder, token_encoder=self.token_encoder
        )
        self.search_custom = DRIFTSearchCustom(
            model=self.chat_model, context_builder=self.context_builder_custom, token_encoder=self.token_encoder
        )


    def _get_description_embedding_store(self):
        description_embedding_store = LanceDBVectorStore(
        collection_name="default-entity-description",
        )
        description_embedding_store.connect(db_uri=LANCEDB_URI)
        return description_embedding_store
    def _get_full_content_embedding_store(self):
        full_content_embedding_store = LanceDBVectorStore(
            collection_name="default-community-full_content",
            )
        full_content_embedding_store.connect(db_uri=LANCEDB_URI)
        return full_content_embedding_store
    
    def _read_community_reports(self, input_dir: str, ):
        """Embeds the full content of the community reports and saves the DataFrame with embeddings to the output path."""
        input_path = Path(input_dir) / f"{self.community_report_table}.parquet"
        return pd.read_parquet(input_path)
    def _get_reports(self):
        report_df = self._read_community_reports(self.input_dir)
        reports = read_indexer_reports(
            report_df,
            self.community_df,
            COMMUNITY_LEVEL,
            content_embedding_col="full_content_embeddings",
        )
        read_indexer_report_embeddings(reports, self.full_content_embedding_store)
        return reports
    async def drift_search(self,query):
        resp =await self.search.search(query)
        answer=resp.response
        context=resp.context_data 
        all_texts = []

        for question, data in context.items():
            sources = data.get('sources')
            if sources is not None and 'text' in sources.columns:
                all_texts.extend(sources['text'].tolist())
        citations = list(set(all_texts))
        return re.sub(r"\[Data:.*?\]", "", answer), []
    async def drift_search_custom(self,query):
        resp =await self.search_custom.search(query)
        answer=resp.response
        context=resp.context_data 
        all_texts = []

        for question, data in context.items():
            sources = data.get('sources')
            if sources is not None and 'text' in sources.columns:
                all_texts.extend(sources['text'].tolist())
        citations = list(set(all_texts))
        return re.sub(r"\[Data:.*?\]", "", answer), []

            

