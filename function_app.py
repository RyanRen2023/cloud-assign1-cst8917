from io import BytesIO
from PIL import Image
import azure.functions as func
import logging

import azure.durable_functions as df
import os
from azure.storage.blob import BlobServiceClient
from importlib_metadata import metadata


VALID_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]


def is_valid_image(blob_name):
    return any(blob_name.lower().endswith(ext) for ext in VALID_EXTENSIONS)


my_app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)
# Initialize BlobServiceClient using the connection string from environment variables
# Ensure the environment variable 'cst8917assignsa_STORAGE' is set in local.settings
blob_service_client = BlobServiceClient.from_connection_string(
    os.environ["cst8917assignsa_STORAGE"]
)


@my_app.blob_trigger(
    arg_name="myblob", path="images-input/{name}", connection="cst8917assignsa_STORAGE"
)
@my_app.durable_client_input(client_name="client")
async def blob_trigger(myblob: func.InputStream, client: df.DurableOrchestrationClient):
    logging.info(
        f"Python blob trigger function processed blob"
        f"Name: {myblob.name}"
        f"Blob Size: {myblob.length} bytes"
    )
    blob_name = myblob.name.split("/")[-1]
    if not is_valid_image(blob_name):
        logging.warning(f"Ignored non-image file: {blob_name}")
        return
    logging.info(f"Trigger received valid image: {blob_name} ({myblob.length} bytes)")

    # Start orchestration and pass the blob name
    instance_id = await client.start_new("orchestrator_function", None, blob_name)
    logging.info(
        f"Started orchestration with ID = '{instance_id}' for blob = '{blob_name}'"
    )


# Orchestrator function definition
@my_app.orchestration_trigger(context_name="context")
def orchestrator_function(context: df.DurableOrchestrationContext):
    # Step 1: Get the blob name from the trigger input
    blob_name = context.get_input()

    # Step 2: Call the activity function to extract image metadata
    metadata = yield context.call_activity("extract_metadata_activity", blob_name)

    # Step 3: Call the activity function to store metadata in Azure SQL Database
    yield context.call_activity("store_metadata_activity", metadata)

    # Step 4: Return a completion message
    return f"Image '{blob_name}' processed successfully."


@my_app.activity_trigger(input_name="blobName")
def extract_metadata_activity(blobName: str):
    logging.info(f"[extract_metadata_activity] Processing: {blobName}")

    try:
        # Access the 'images-input' container
        container_client = blob_service_client.get_container_client("images-input")
        blob_client = container_client.get_blob_client(blobName)

        # Download the image blob as bytes
        blob_data = blob_client.download_blob().readall()
        image_stream = BytesIO(blob_data)

        # Load image using Pillow
        image = Image.open(image_stream)

        # Extract metadata
        metadata = {
            "filename": blobName,
            "format": image.format,
            "width": image.width,
            "height": image.height,
            "size_kb": round(len(blob_data) / 1024, 2),
        }

        logging.info(f"[extract_metadata_activity] Metadata: {metadata}")
        return metadata

    except Exception as e:
        logging.error(f"[extract_metadata_activity] Error: {str(e)}")
        raise


@my_app.activity_trigger(input_name="metadata")
@my_app.sql_output(
    arg_name="row",
    command_text="[dbo].[ImageMetadata]",
    connection_string_setting="SqlConnectionString"
)
def store_metadata_activity(metadata: dict, row: func.Out[func.SqlRow]) -> dict:
    logging.info(f"[store_metadata_activity] Storing metadata: {metadata}")
    sql_row = func.SqlRow.from_dict(metadata)
    row.set(sql_row)
    return metadata  # Let the output binding use this return value