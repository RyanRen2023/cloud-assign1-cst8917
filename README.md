# CST8917 Assignment 1: Durable Workflow for Image Metadata Processing

**Due Date**: Saturday, July 19, 2025, 11:59 PM  
**Author**: Xihai Ren  
**Course**: CST8917 

---

## Objective

Build a **serverless image metadata processing pipeline** using **Azure Durable Functions** in **Python**. This assignment simulates a real-world event-driven system and helps you gain experience with blob triggers, activity functions, and output bindings.

---

## Scenario

A fictional content moderation team wants to analyze metadata of user-uploaded images. Your Azure Durable Functions app should:

- Automatically **trigger** when a new image is uploaded to blob storage.
- **Extract metadata** such as file size, format, and dimensions.
- **Store** the metadata into an **Azure SQL Database**.

---

## Workflow Overview

### Step 1: Blob Trigger (Client Function)
- A function triggered by a new image in the `images-input` blob container.
- Acceptable formats: `.jpg`, `.jpeg`, `.png`, `.gif`.
- Validates file format and starts the orchestration process.

### Step 2: Orchestrator Function
The orchestrator coordinates the entire workflow:
1. Receives the blob name from the trigger
2. Calls an activity function to extract metadata
3. Calls another activity function to store metadata in SQL DB
4. Returns a completion message

### Step 3: Activity Function – Extract Metadata
Extract the following metadata from each image:
- `filename`: File name
- `format`: Image format (JPEG, PNG, etc.)
- `width`: Width in pixels
- `height`: Height in pixels
- `size_kb`: File size in kilobytes (KB)

### Step 4: Activity Function – Store Metadata
- Store metadata to Azure SQL DB using **output binding**
- Target table: `[dbo].[ImageMetadata]`

---

## Technology Stack

- **Azure Durable Functions** (Python)
- **Azure Blob Storage** - Image storage and triggers
- **Azure SQL Database** - Metadata storage
- **Pillow (PIL)** - Image processing and metadata extraction
- **Azure Storage Blob SDK** - Blob operations

---

## Dependencies

Key dependencies include:
- `azure-functions`
- `azure-functions-durable`
- `azure-storage-blob`
- `Pillow`
- `cryptography`
- `azure-identity`

See `requirements.txt` for complete list.

---

## Setup and Deployment

### Prerequisites
- Azure subscription
- Azure CLI installed
- Python 3.8+ installed
- Azure Functions Core Tools

### 1. Create Azure Resources

#### SQL Server and Database
```bash
# Create SQL Server
az sql server create \
  --name cst8917dbserver \
  --resource-group cst8917assign-rg \
  --location canadacentral \
  --admin-user xradmin \
  --admin-password password123!

# Create Database
az sql db create \
  --name cst8917sqldb \
  --server cst8917dbserver \
  --resource-group cst8917assign-rg \
  --service-objective Basic

# Configure Firewall
az sql server firewall-rule create \
  --name AllowAzure \
  --server cst8917dbserver \
  --resource-group cst8917assign-rg \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Get Connection String
az sql db show-connection-string \
  --name cst8917sqldb \
  --server cst8917dbserver \
  --client ado.net
```

#### Storage Account
```bash
# Create Storage Account
az storage account create \
  --name storageaccount8917xr \
  --resource-group cst8917assign-rg \
  --location canadacentral \
  --sku Standard_LRS

# Create Blob Container
az storage container create \
  --name images-input \
  --account-name storageaccount8917xr
```

### 2. Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/RyanRen2023/cloud-assign1-cst8917.git
   cd cloud-assign1-cst8917
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure local settings**
   - Copy `local.settings.json.example` to `local.settings.json`
   - Update connection strings with your Azure resources

4. **Run locally**
   ```bash
   func start
   ```

### 3. Deploy to Azure

```bash
# Deploy to Azure Functions
func azure functionapp publish <your-function-app-name>
```

---

## Database Schema

The application expects the following table structure in Azure SQL Database:

```sql
CREATE TABLE [dbo].[ImageMetadata] (
    [filename] NVARCHAR(255) NOT NULL,
    [format] NVARCHAR(50) NOT NULL,
    [width] INT NOT NULL,
    [height] INT NOT NULL,
    [size_kb] DECIMAL(10,2) NOT NULL,
    [timestamp] DATETIME2 DEFAULT GETDATE()
);
```

---

## Project Structure

```
cloud-assign1-cst8917/
├── function_app.py          # Main Azure Functions code
├── requirements.txt         # Python dependencies
├── host.json               # Azure Functions host configuration
├── local.settings.json     # Local development settings
├── README.md               # This file
├── requirement.md          # Assignment requirements
├── .funcignore            # Azure Functions ignore file
└── .gitignore             # Git ignore file
```

---

## Configuration

### Environment Variables
- `cst8917assignsa_STORAGE`: Azure Storage connection string
- `SqlConnectionString`: Azure SQL Database connection string
- `AzureWebJobsStorage`: Azure Functions storage connection string

### Blob Container
- **Container Name**: `images-input`
- **Supported Formats**: `.jpg`, `.jpeg`, `.png`, `.gif`

---

## Testing

1. **Upload an image** to the `images-input` blob container
2. **Monitor the function logs** in Azure Portal
3. **Check the SQL database** for stored metadata
4. **Verify the orchestration** completed successfully

### Test Images
You can test with any standard image formats:
- JPEG images (.jpg, .jpeg)
- PNG images (.png)
- GIF images (.gif)


---

## Demo

[Watch Demo](https://youtu.be/w2UwWm7jFu0)


---
