# Vertex AI Setup Guide for Novel-to-Comic

This guide will help you set up Vertex AI for the Novel-to-Comic project using your Google Cloud project `novel-to-comic`.

## 🎯 **What You Need from Google Cloud Platform**

### **1. Project Information**

- **Project ID**: `novel-to-comic` (you already have this)
- **Location**: `us-central1` (recommended for best performance)

### **2. Authentication Method**

Choose one of these options:

#### **Option A: Service Account (Recommended for Production)**

- Service account key file (JSON)
- IAM permissions

#### **Option B: Application Default Credentials (Recommended for Development)**

- Google Cloud CLI authentication
- No key files needed

## 📋 **Step-by-Step Setup**

### **Step 1: Access Google Cloud Console**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Make sure you're in the `novel-to-comic` project
3. Verify billing is enabled (required for Vertex AI)

### **Step 2: Enable Required APIs**

In the Google Cloud Console:

1. **Navigate to APIs & Services > Library**
2. **Search for and enable these APIs:**
   - `Vertex AI API` (aiplatform.googleapis.com)
   - `Cloud Storage API` (storage.googleapis.com)
   - `IAM Service Account Credentials API` (iamcredentials.googleapis.com)

**Or use gcloud CLI:**

```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable iamcredentials.googleapis.com
```

### **Step 3: Set Up Authentication**

#### **Option A: Service Account (Production)**

1. **Create Service Account:**

   - Go to **IAM & Admin > Service Accounts**
   - Click **Create Service Account**
   - Name: `novel-to-comic-sa`
   - Description: `Service account for Novel-to-Comic project`

2. **Grant Permissions:**

   - Click on the created service account
   - Go to **Permissions** tab
   - Click **Grant Access**
   - Add these roles:
     - `Vertex AI User`
     - `Storage Object Viewer`

3. **Create Key:**
   - Go to **Keys** tab
   - Click **Add Key > Create New Key**
   - Choose **JSON** format
   - Download the key file
   - Save it as `~/novel-to-comic-key.json`

#### **Option B: Application Default Credentials (Development)**

1. **Install Google Cloud CLI:**

   ```bash
   # macOS
   brew install google-cloud-sdk

   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate:**
   ```bash
   gcloud auth login
   gcloud config set project novel-to-comic
   gcloud auth application-default login
   ```

### **Step 4: Set Environment Variables**

#### **For Service Account:**

```bash
export GOOGLE_APPLICATION_CREDENTIALS="~/novel-to-comic-key.json"
export GOOGLE_CLOUD_PROJECT="novel-to-comic"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

#### **For Application Default Credentials:**

```bash
export GOOGLE_CLOUD_PROJECT="novel-to-comic"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

### **Step 5: Test the Setup**

Run the test script:

```bash
uv run python test_vertexai.py
```

## 🔍 **How to Get Information from Google Cloud Console**

### **Finding Your Project ID:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Look at the project selector at the top
3. Your project ID is `novel-to-comic`

### **Finding Available Locations:**

1. Go to **Vertex AI > Model Garden**
2. Look for the location dropdown
3. Recommended: `us-central1` (best performance and availability)

### **Checking API Status:**

1. Go to **APIs & Services > Enabled APIs**
2. Verify these are enabled:
   - `Vertex AI API`
   - `Cloud Storage API`
   - `IAM Service Account Credentials API`

### **Checking Billing:**

1. Go to **Billing**
2. Ensure billing is enabled for the project
3. Vertex AI requires billing to be enabled

### **Checking Permissions:**

1. Go to **IAM & Admin > IAM**
2. Find your user/service account
3. Verify it has `Vertex AI User` role

## 🚀 **Running the Novel-to-Comic Generator**

Once setup is complete:

```bash
# Test the setup
uv run python test_vertexai.py

# Run the full comic generator
uv run python demo.py
```

## 💡 **Benefits of Vertex AI**

- **Higher Rate Limits**: Much higher than free Gemini API
- **Better Performance**: Google Cloud infrastructure
- **Enterprise Features**: Logging, monitoring, security
- **Cost Control**: Pay-per-use with quotas
- **Same API**: Uses the same `google-genai` library

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **"Permission denied"**

   - Check IAM roles
   - Verify service account permissions

2. **"API not enabled"**

   - Enable required APIs in Google Cloud Console

3. **"Billing not enabled"**

   - Enable billing for the project

4. **"Authentication failed"**
   - Check credentials file path
   - Verify service account key is valid

### **Getting Help:**

- Check the test output: `uv run python test_vertexai.py`
- Review Google Cloud Console logs
- Check the [Vertex AI documentation](https://cloud.google.com/vertex-ai/docs)
