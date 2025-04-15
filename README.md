# mini-demo-astradb-glean

Demo showing how to index [Astra DB](https://docs.datastax.com/en/astra-db-serverless/index.html) data into Glean.

You can run this tutorial entirely in a google colab, or run it locally by following the instructions below.

## Work in a Colab

[![Open In Colab](https://img.shields.io/badge/Open%20in%20Colab-blue?logo=google-colab&style=for-the-badge)](https://colab.research.google.com/github/datastaxdevs/mini-demo-astradb-glean/blob/main/AstraDB_Glean_Integration.ipynb)

## Run Locally

[![Run Locally](https://img.shields.io/badge/Run%20Locally-python3-blue?style=for-the-badge)](#)


### 1. Set up Astra DB

ℹ️ See the [Astra Reference documentation](https://docs.datastax.com/en/astra-db-serverless/databases/create-database.html).


`✅ 1.1`: Create an Astra account

Access [https://astra.datastax.com](https://astra.datastax.com) and register with `Google` or `Github` account.

![](https://github.com/datastaxdevs/mini-demo-astradb-glean/blob/main/images/01-login.png?raw=true)


`✅ 1.2`: Create a Database in Astra DB

Get to the databases dashboard (by clicking on Databases in the left-hand navigation bar, expanding it if necessary), and click the `[Create Database]` button on the right.

![](https://github.com/datastaxdevs/mini-demo-astradb-glean/blob/main/images/02-create-db.png?raw=true)


**ℹ️ Field Description**

| Field                                      | Description                                                                                                                                                                                                                                   |
|--------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Vector Database vs Serverless Database** | Choose `Vector Database`. In june 2023, Cassandra introduced the support of vector search to enable Generative AI use cases.                                                                                                                   |
| **Database name**                          | Database names are permanent. They must start and end with a letter or number, and they can contain no more than 50 characters, including letters, numbers, and the special characters `& + - _ ( ) < > . , @`. It is recommended to have a database for each of your applications. The free tier is limited to 5 databases. |
| **Cloud Provider**                         | Choose whatever you like. Click a cloud provider logo, pick an Area in the list and finally pick a region. We recommend choosing a region that is closest to you to reduce latency. In the free tier, there is very little difference.            |
| **Cloud Region**                           | Pick a region close to you, among those available for the selected cloud provider and your plan.      

If all fields are filled properly, clicking the "Create Database" button will start the process.

![](https://github.com/datastaxdevs/mini-demo-astradb-glean/blob/main/images/03-pending-db.png?raw=true)

It should take a couple of minutes for your database to become `Active`.

![](https://github.com/datastaxdevs/mini-demo-astradb-glean/blob/main/images/04-active-db.png?raw=true)

`✅ 1.3`: Create an Astra Database token

To [connect to your database](https://docs.datastax.com/en/astra-db-serverless/get-started/quickstart.html#create-a-database-and-store-your-credentials), you need the **API endpoint** and a **Database token**.

The API endpoint is available on the database screen, there is a little icon to copy the URL in your clipboard. (it should look like `https://<db-id>-<db-region>.apps.astra.datastax.com`).

![](https://github.com/datastaxdevs/mini-demo-astradb-glean/blob/main/images/05-create-token-db.png?raw=true)

To get a token click the `[Generate Token]` button on the right. It will generate a token that you can copy to your clipboard.

### 2. Obtain a Glean token

> [Glean Documentation](https://developers.glean.com/indexing#authentication)

Admins can manage Glean API tokens via the API tokens page within Workspace Settings:

```
Workspace > Setup > API tokens > Indexing tokens tab
```

As a Glean admin, create a token and assign permissions (or have an admin do it for you).

### 3. Installation

- `✅ 3.1`: Create and activate a virtual environment. You need Python version 3.9 or higher.

```console
python3 -m venv my_virtual_env
```

_macOS/Linux:_
```
source my_virtual_env/bin/activate
```

_Windows:_
```
my_virtual_env\Scripts\activate
```

- `✅ 3.2`:Install the dependencies:

```console
pip install -r requirements.txt
```

## 4. Create environment file

Copy `.env.example` as `.env`, and edit its content with the Astra DB and Glean credentials:

```ini
# Astra Configuration
export ASTRA_DB_APPLICATION_TOKEN=<change_me>
export ASTRA_DB_API_ENDPOINT=<change_me>
export ASTRA_DB_COLLECTION_NAME="plain_collection"
# export ASTRA_DB_KEYSPACE="default_keyspace"  # Optional

# Glean Configuration
export GLEAN_CUSTOMER=<you>
export GLEAN_DATASOURCE_NAME=<change_me>
export GLEAN_API_TOKEN=<change_me>
```

## 5. Run the script

```console
python3 astra-glean-import-job.py
```

## Wrap up and more information

Congratulations: you have indexed data from an Astra DB collection into Glean!

You can inspect the Astra DB collection in your Astra dashboard: navigate to the database and find the "Data explorer" tab to locate your collection.

You can perform a test with Glean: search for the content you just indexed and verify the response contains information coming from the inserted dataset.

ℹ️ [Glean integration page](https://docs.datastax.com/en/astra-db-serverless/integrations/glean.html) on Astra DB documentation.
