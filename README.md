# mini-demo-astradb-glean

Demo showing how to index [Astra DB](https://docs.datastax.com/en/astra-db-serverless/index.html) data into Glean.

You can run this tutorial entirely in a google colab, or run it locally by following the instructions below.

## Work in a Colab

[![Open In Colab](https://img.shields.io/badge/Open%20in%20Colab-blue?logo=google-colab&style=for-the-badge)](https://colab.research.google.com/github/datastaxdevs/mini-demo-astradb-glean/blob/main/AstraDB_Glean_Integration.ipynb)

## Run Locally

[![Run Locally](https://img.shields.io/badge/Run%20Locally-python3-blue?style=for-the-badge)](#)


### 1.1 Set up Astra DB

ℹ️ See the [Astra Reference documentation](https://docs.datastax.com/en/astra-db-serverless/databases/create-database.html).


`✅ 1.1.a`: Create an Astra ACCOUNT

Access [https://astra.datastax.com](https://astra.datastax.com) and register with `Google` or `Github` account.

![](https://github.com/datastaxdevs/mini-demo-astradb-glean/blob/main/images/01-login.png?raw=true)


`✅ 1.1.b`: Create a Database in Astra DB

Get to the databases dashboard (by clicking on Databases in the left-hand navigation bar, expanding it if necessary), and click the `[Create Database]` button on the right.

![](https://github.com/datastaxdevs/mini-demo-astradb-glean/blob/main/images/02-create-db.png?raw=true)


- **ℹ️ Field Description**

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

`✅ 1.1.c`: Create an Astra TOKEN

To [connect to your database](https://docs.datastax.com/en/astra-db-serverless/get-started/quickstart.html#create-a-database-and-store-your-credentials), you need the **API endpoint** and a **Database token**.

The API endpoint is available on the database screen, there is a little icon to copy the URL in your clipboard. (it should look like `https://<db-id>-<db-region>.apps.astra.datastax.com`).

![](https://github.com/datastaxdevs/mini-demo-astradb-glean/blob/main/images/05-create-token-db.png?raw=true)

To get a token click the `[Generate Token]` button on the right. It will generate a token that you can copy to your clipboard.

## 2. Installation

### 2.1 Python Environment

- `✅ 2.1.a`: Create and activate a virtual environment. You need Python version 3.9 or higher.

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

- `✅ 2.1.b`:Install the dependencies:

```console
pip install -r requirements.txt
```

- `✅ 2.1.c`: Create an environment file (`.env`):

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

## 3. Run the script

```console
python3 astra-glean-import-job.py
```

## 4. More information

ℹ️ [Glean integration page](https://docs.datastax.com/en/astra-db-serverless/integrations/glean.html) on Astra DB documentation.
