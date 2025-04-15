import os

from astrapy import DataAPIClient
from colorama import Fore, Style
from datasets import load_dataset
from dotenv import load_dotenv

import glean_indexing_api_client as indexing_api
from glean_indexing_api_client.api import datasources_api, documents_api
from glean_indexing_api_client.model.custom_datasource_config import (
    CustomDatasourceConfig,
)
from glean_indexing_api_client.model.object_definition import ObjectDefinition
from glean_indexing_api_client.model.index_document_request import IndexDocumentRequest
from glean_indexing_api_client.model.document_definition import DocumentDefinition
from glean_indexing_api_client.model.content_definition import ContentDefinition
from glean_indexing_api_client.model.document_permissions_definition import (
    DocumentPermissionsDefinition,
)


# Load environment variables from .env
load_dotenv()

ASTRA_DB_APPLICATION_TOKEN = os.environ["ASTRA_DB_APPLICATION_TOKEN"]
ASTRA_DB_API_ENDPOINT = os.environ["ASTRA_DB_API_ENDPOINT"]
ASTRA_DB_COLLECTION_NAME = os.environ["ASTRA_DB_COLLECTION_NAME"]
ASTRA_DB_KEYSPACE = os.getenv("ASTRA_DB_KEYSPACE")

GLEAN_API_TOKEN = os.environ["GLEAN_API_TOKEN"]
GLEAN_CUSTOMER = os.environ["GLEAN_CUSTOMER"]
GLEAN_DATASOURCE_NAME = os.environ["GLEAN_DATASOURCE_NAME"]


print(f"{Fore.GREEN}============================={Style.RESET_ALL}")
print(f"{Fore.GREEN} ASTRADB - GLEAN INTEGRATION {Style.RESET_ALL}")
print(f"{Fore.GREEN}============================={Style.RESET_ALL}\n")

# Initialize Astra DB client
client = DataAPIClient(callers=[("glean", "1.0")])
database = client.get_database(
    ASTRA_DB_API_ENDPOINT,
    token=ASTRA_DB_APPLICATION_TOKEN,
    keyspace=ASTRA_DB_KEYSPACE,
)
print(
    f"{Fore.CYAN}[ OK ] - Credentials are OK, your database name is "
    f"{Style.RESET_ALL}{database.name()}{Fore.CYAN}."
)

# Create collection
source_collection = database.create_collection(ASTRA_DB_COLLECTION_NAME)
print(
    f"{Fore.CYAN}[ OK ] - Collection {Style.RESET_ALL}{source_collection.name}"
    f"{Fore.CYAN} is ready{Style.RESET_ALL}{Fore.CYAN}."
)

# Load philosophers dataset
print(f"{Fore.CYAN}[INFO] - Downloading data from Hugging Face 🤗.{Style.RESET_ALL}")
philo_dataset = load_dataset("datastax/philosopher-quotes")["train"]
print(f"{Fore.CYAN}[ OK ] - Dataset loaded in memory.{Style.RESET_ALL}")
print(f"{Fore.CYAN}[INFO] - Sample record: {Style.RESET_ALL}{philo_dataset[16]}")


def load_to_astra_db(data_to_insert, collection):
    """Load all of the provided data into a collection."""
    def split_tags(t):
        return [tag for tag in (t or "").split(";") if tag]

    documents_to_insert = [
        {
            **item,
            **{"_id": index, "tags": split_tags(item["tags"])},
        }
        for index, item in enumerate(data_to_insert)
    ]
    collection.insert_many(documents_to_insert)


# Empty the collection before inserting fresh data
# (WARNING: it may wipe out actual data. We are doing it for DEMO PURPOSES here.)
source_collection.delete_many({})
print(f"{Fore.CYAN}[ OK ] - Collection has been emptied.{Style.RESET_ALL}")

# Insert documents into Astra DB
philo_count = len(philo_dataset)
print(
    f"{Fore.CYAN}[INFO] - Inserting {philo_count} documents into Astra DB..."
    f"{Style.RESET_ALL}"
)
load_to_astra_db(philo_dataset, source_collection)
print(f"{Fore.CYAN}[ OK ] - Insertion finished.{Style.RESET_ALL}")

# Setup Glean API
GLEAN_API_ENDPOINT = f"https://{GLEAN_CUSTOMER}-be.glean.com/api/index/v1"
print(
    f"{Fore.CYAN}[INFO] - Glean API setup, endpoint is:"
    f"{Style.RESET_ALL} {GLEAN_API_ENDPOINT}"
)

# Initialize Glean client
configuration = indexing_api.Configuration(
    host=GLEAN_API_ENDPOINT, access_token=GLEAN_API_TOKEN
)
api_client = indexing_api.ApiClient(configuration)
datasource_api = datasources_api.DatasourcesApi(api_client)
print(f"{Fore.CYAN}[ OK ] - Glean client initialized{Style.RESET_ALL}")

# Create and register datasource in Glean
datasource_config = CustomDatasourceConfig(
    name=GLEAN_DATASOURCE_NAME,
    display_name="AstraDB Collection DataSource",
    datasource_category="PUBLISHED_CONTENT",
    url_regex=f"^{ASTRA_DB_API_ENDPOINT}",
    object_definitions=[
        ObjectDefinition(doc_category="PUBLISHED_CONTENT", name="AstraVectorEntry")
    ],
)

try:
    datasource_api.adddatasource_post(datasource_config)
    print(
        f"{Fore.GREEN}[ OK ] - DataSource has been created!"
        f"{Style.RESET_ALL}{Fore.GREEN}."
    )
except indexing_api.ApiException as e:
    print(
        f"{Fore.RED}[ ERROR ] - Error creating datasource: "
        f"{e}{Style.RESET_ALL}{Fore.GREEN}."
    )


def index_astra_db_document_into_glean(astra_document):
    """Index one Astra DB document into Glean."""
    document_id = str(astra_document["_id"])
    title = f"{astra_document['author']} quote_{astra_document['_id']}"
    body_text = astra_document["quote"]
    datasource_name = GLEAN_DATASOURCE_NAME
    request = IndexDocumentRequest(
        document=DocumentDefinition(
            datasource=datasource_name,
            title=title,
            id=document_id,
            view_url=ASTRA_DB_API_ENDPOINT,
            body=ContentDefinition(mime_type="text/plain", text_content=body_text),
            permissions=DocumentPermissionsDefinition(allow_anonymous_access=True),
        )
    )
    documents_api_client = documents_api.DocumentsApi(api_client)
    try:
        documents_api_client.indexdocument_post(request)
    except indexing_api.ApiException as e:
        print(f"{Fore.RED}Error indexing document {document_id}: {e}{Style.RESET_ALL}")


def index_documents_to_glean(collection):
    """Index all documents from an Astra DB collection to Glean."""
    total_docs = collection.count_documents({}, upper_bound=1000)
    print(
        f"{Fore.CYAN}[INFO] - Indexing {total_docs} "
        f"documents into Glean...{Style.RESET_ALL}"
    )
    for doc in collection.find():
        try:
            index_astra_db_document_into_glean(doc)
        except Exception as error:
            print(
                f"{Fore.RED}Error indexing document "
                f"{doc['_id']}: {error}{Style.RESET_ALL}"
            )
    print(f"{Fore.CYAN}[ OK ] - Indexing finished.{Style.RESET_ALL}")


# Use the function to index documents into Glean
index_documents_to_glean(source_collection)

print(f"{Fore.GREEN}Import job completed successfully!{Style.RESET_ALL}")
