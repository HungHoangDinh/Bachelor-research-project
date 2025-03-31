import os
from pathlib import Path

import pandas as pd
import tiktoken

from graphrag.config.enums import ModelType
from graphrag.config.models.drift_search_config import DRIFTSearchConfig
from graphrag.config.models.language_model_config import LanguageModelConfig
from graphrag.language_model.manager import ModelManager
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