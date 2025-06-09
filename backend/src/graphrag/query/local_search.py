import os
import re
import pandas as pd
import tiktoken
from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.indexer_adapters import (
    read_indexer_covariates,
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.question_gen.local_gen import LocalQuestionGen
from graphrag.query.structured_search.local_search.mixed_context import (
    LocalSearchMixedContext,
)
from dotenv import load_dotenv
load_dotenv()
from graphrag.query.structured_search.local_search.search import LocalSearch
from .custom.custom_prompt import LOCAL_SEARCH_SYSTEM_PROMPT
from graphrag.vector_stores.lancedb import LanceDBVectorStore
from graphrag.config.enums import ModelType
from graphrag.config.models.language_model_config import LanguageModelConfig
from graphrag.language_model.manager import ModelManager
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
class GraphragLocalSearch:
    def __init__(self):
        self.api_key = os.environ.get("GRAPHRAG_API_KEY")
        self.llm_model = os.environ.get("GRAPHRAG_LLM_MODEL")
        self.embedding_model = os.environ.get("GRAPHRAG_EMBEDDING_MODEL")
        self.input_dir = INPUT_DIR
        self.lancedb_uri = LANCEDB_URI
        self.community_report_table = COMMUNITY_REPORT_TABLE
        self.entity_table = ENTITY_TABLE
        self.community_table = COMMUNITY_TABLE
        self.relationship_table = RELATIONSHIP_TABLE
        self.covariate_table = COVARIATE_TABLE
        self.text_unit_table = TEXT_UNIT_TABLE
        self.community_level = COMMUNITY_LEVEL
        self.entities=self._read_entities()
        self.description_embedding_store=self._connect_db()
        self.relationships=self._read_relationships()
        self.reports=self._read_community_reports()
        self.text_units=self._read_text_units()
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
        self.context_builder = LocalSearchMixedContext(
            community_reports=self.reports,
            text_units=self.text_units,
            entities=self.entities,
            relationships=self.relationships,
            entity_text_embeddings=self.description_embedding_store,
            embedding_vectorstore_key=EntityVectorStoreKey.ID,  # if the vectorstore uses entity title as ids, set this to EntityVectorStoreKey.TITLE
            text_embedder=self.text_embedder,
            token_encoder=self.token_encoder,
        )
        self.local_context_params = {
            "text_unit_prop": 0.5,
            "community_prop": 0.1,
            "conversation_history_max_turns": 5,
            "conversation_history_user_turns_only": True,
            "top_k_mapped_entities": 10,
            "top_k_relationships": 10,
            "include_entity_rank": False,
            "include_relationship_weight": True,
            "include_community_rank": False,
            "return_candidate_context": False,
            "embedding_vectorstore_key": EntityVectorStoreKey.ID,  # set this to EntityVectorStoreKey.TITLE if the vectorstore uses entity title as ids
            "max_tokens": 24_000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 5000)
        }
        self.model_params = {
            "max_tokens": 8_000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 1000=1500)
            "temperature": 0.0,
        }
        self.search_engine = LocalSearch(
            model=self.chat_model,
            context_builder=self.context_builder,
            token_encoder=self.token_encoder,
            model_params=self.model_params,
            context_builder_params=self.local_context_params,
            response_type="multiple paragraphs",  # free form text describing the response type and format, can be anything, e.g. prioritized list, single paragraph, multiple paragraphs, multiple-page report
        )
        self.search_engine_custom=LocalSearch(
            model=self.chat_model,
            system_prompt=LOCAL_SEARCH_SYSTEM_PROMPT,
            context_builder=self.context_builder,
            token_encoder=self.token_encoder,
            model_params=self.model_params,
            context_builder_params=self.local_context_params,
        )
        self.question_generator = LocalQuestionGen(
            model=self.chat_model,
            context_builder=self.context_builder,
            token_encoder=self.token_encoder,
            llm_params=self.model_params,
            context_builder_params=self.local_context_params,
        )

    def _read_entities(self):
        entity_df = pd.read_parquet(f"{self.input_dir}/{self.entity_table}.parquet")
        community_df = pd.read_parquet(f"{self.input_dir}/{self.community_table}.parquet")
        entities = read_indexer_entities(entity_df, community_df, self.community_level)
        print(f"Number of entities: {len(entities)}")
        return entities
    def _connect_db(self):
        # load description embeddings to an in-memory lancedb vectorstore
        # to connect to a remote db, specify url and port values.
        description_embedding_store = LanceDBVectorStore(
            collection_name="default-entity-description",
        )
        description_embedding_store.connect(db_uri=self.lancedb_uri)
        return description_embedding_store
    def _read_relationships(self):
        relationship_df = pd.read_parquet(f"{self.input_dir}/{self.relationship_table}.parquet")
        relationships = read_indexer_relationships(relationship_df)
        print(f"Number of relationships: {len(relationships)}")
        return relationships
    def _read_community_reports(self):
        report_df = pd.read_parquet(f"{self.input_dir}/{self.community_report_table}.parquet")
        community_df = pd.read_parquet(f"{self.input_dir}/{self.community_table}.parquet")
        reports = read_indexer_reports(report_df, community_df, self.community_level)
        print(f"Number of community reports: {len(reports)}")
        return reports
    def  _read_text_units(self):
        text_unit_df = pd.read_parquet(f"{self.input_dir}/{self.text_unit_table}.parquet")
        text_units = read_indexer_text_units(text_unit_df)
        print(f"Number of text units: {len(text_units)}")
        print(text_units)
        return text_units
    async def local_search(self, query):
        result = await self.search_engine.search(query)
        answer=result.response
        citations=[]

        for _, row in result.context_data["sources"].iterrows():
            citations.append(row["text"])
        answer=re.sub(r"\[Data:.*?\]", "", answer)

        return answer,citations
    async def local_search_custom(self, query):
        result = await self.search_engine_custom.search(query)
        answer=result.response
        citations=[]

        for _, row in result.context_data["sources"].iterrows():
            citations.append(row["text"])
        answer=re.sub(r"\[Data:.*?\]", "", answer)
        return answer,citations
    async def question_gen(self, query):
        candidate_questions = await self.question_generator.agenerate(
            question_history=[query], context_data=None, question_count=5
        )
        return candidate_questions.response
    


    
    
  
    
  