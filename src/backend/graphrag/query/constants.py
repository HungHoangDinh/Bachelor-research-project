from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.environ["OPENAI_API_KEY"]
LLM_MODEL = "gpt-4o-mini" 
EMBEDDING_MODEL ="text-embedding-3-small"
INPUT_DIR = "src/backend/graphrag/graphrag_db/output"
LANCEDB_URI = f"{INPUT_DIR}/lancedb"
COMMUNITY_REPORT_TABLE = "create_final_community_reports"
ENTITY_TABLE = "create_final_nodes"
ENTITY_EMBEDDING_TABLE = "create_final_entities"
RELATIONSHIP_TABLE = "create_final_relationships"
COVARIATE_TABLE = "create_final_covariates"
TEXT_UNIT_TABLE = "create_final_text_units"
COMMUNITY_LEVEL = 2
COMMUNITY_TABLE = "create_final_communities"