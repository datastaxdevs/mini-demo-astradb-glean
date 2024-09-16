import os
from dotenv import load_dotenv
from getpass import getpass
import pandas as pd
from astrapy import DataAPIClient
from ipywidgets import IntProgress
from IPython.display import display
import json
import glean_indexing_api_client as indexing_api
from glean_indexing_api_client.api import datasources_api, documents_api
from glean_indexing_api_client.model.custom_datasource_config import CustomDatasourceConfig
from glean_indexing_api_client.model.object_definition import ObjectDefinition
from glean_indexing_api_client.model.index_document_request import IndexDocumentRequest
from glean_indexing_api_client.model.document_definition import DocumentDefinition
from glean_indexing_api_client.model.content_definition import ContentDefinition
from glean_indexing_api_client.model.document_permissions_definition import DocumentPermissionsDefinition
from datasets import load_dataset

# Load environment variables from .env
load_dotenv()

ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
GLEAN_API_TOKEN       = os.getenv("GLEAN_API_TOKEN")
GLEAN_CUSTOMER        = os.getenv("GLEAN_CUSTOMER")
GLEAN_DATASOURCE_NAME = os.getenv("GLEAN_DATASOURCE_NAME")

# Initialize Astra DB client
client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
database = client.get_database(ASTRA_DB_API_ENDPOINT)
print(f"* Credential are OK, your database name is {database.info().name}\n")

# Create collection
plain_collection = database.create_collection("plain_collection", check_exists=False)
print(f"* Collection 'plain_collection' is ready")

# List collections
for coll_desc in database.list_collection_names():
    print(coll_desc)

# Load philosopher dataset
philo_dataset = load_dataset("datastax/philosopher-quotes")["train"]
print("An example entry:")
print(philo_dataset[16])
philo_dataframe = pd.DataFrame.from_dict(philo_dataset)

# Progress bar for loading to Astra
def load_to_astra(df, collection):
    len_df = len(df)
    progress = IntProgress(min=0, max=len_df)
    display(progress)
    for i in range(len_df):
        progress.value += 1
        progress.description = f"{progress.value}/{len_df}"
        try:
            collection.insert_one({
                "_id": i,
                "author": df.loc[i, "author"],
                "quote": df.loc[i, "quote"],
                "tags": df.loc[i, "tags"].split(";") if pd.notna(df.loc[i, "tags"]) else []
            })
        except Exception as error:
            print(f"Error while inserting document {i}: {error}")

# Flush the collection before inserting new data
plain_collection.delete_many({})

# Insert documents into Astra DB
load_to_astra(philo_dataframe, plain_collection)

# Setup Glean API
GLEAN_API_ENDPOINT = f"https://{GLEAN_CUSTOMER}-be.glean.com/api/index/v1"
print("Glean API setup, endpoint is:", GLEAN_API_ENDPOINT)

# Initialize Glean client
configuration = indexing_api.Configuration(host=GLEAN_API_ENDPOINT, access_token=GLEAN_API_TOKEN)
api_client = indexing_api.ApiClient(configuration)
datasource_api = datasources_api.DatasourcesApi(api_client)

# Create and register datasource in Glean
datasource_config = CustomDatasourceConfig(
    name=GLEAN_DATASOURCE_NAME,
    display_name='AstraDB Collection DataSource',
    datasource_category='PUBLISHED_CONTENT',
    url_regex='^https://your_astra_db_url',  # Replace with actual regex
    object_definitions=[
        ObjectDefinition(
            doc_category='PUBLISHED_CONTENT',
            name='AstraVectorEntry'
        )
    ]
)

try:
    datasource_api.adddatasource_post(datasource_config)
    print('DataSource has been created!')
except indexing_api.ApiException as e:
    print(f"Error creating datasource: {e}")

# Function to index Astra documents into Glean
def index_astra_document_into_glean(astra_document):
    document_id = str(astra_document['_id'])
    title = astra_document['author'] + ' quote_' + str(astra_document['_id'])
    body_text = astra_document['quote']
    datasource_name = GLEAN_DATASOURCE_NAME
    request = IndexDocumentRequest(
        document=DocumentDefinition(
            datasource=datasource_name,
            title=title,
            id=document_id,
            view_url="https://your_astra_db_url",
            body=ContentDefinition(mime_type="text/plain", text_content=body_text),
            permissions=DocumentPermissionsDefinition(allow_anonymous_access=True),
        )
    )
    documents_api_client = documents_api.DocumentsApi(api_client)
    try:
        documents_api_client.indexdocument_post(request)
    except indexing_api.ApiException as e:
        print(f"Error indexing document {document_id}: {e}")

# Index documents from Astra DB to Glean
for doc in plain_collection.find():
    index_astra_document_into_glean(doc)
