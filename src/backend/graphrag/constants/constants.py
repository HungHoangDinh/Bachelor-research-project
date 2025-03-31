import os

CUR_DIRECTORY = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')

SRC_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(CUR_DIRECTORY)))
INPUT_DIR =SRC_DIRECTORY+ "/backend/graphrag/graphrag_db/output/"
LANCEDB_URI = f"{INPUT_DIR}/lancedb"

COMMUNITY_REPORT_TABLE = "community_reports"
ENTITY_TABLE = "entities"
COMMUNITY_TABLE = "communities"
RELATIONSHIP_TABLE = "relationships"
COVARIATE_TABLE = "covariates"
TEXT_UNIT_TABLE = "text_units"
COMMUNITY_LEVEL = 2