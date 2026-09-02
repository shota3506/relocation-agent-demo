# Deployment Guide

This guide explains how to provision infrastructure and deploy the agent to Google Cloud (Vertex AI Agent Runtime).

---

## Prerequisites

- **Google Cloud SDK (`gcloud`)** installed and authenticated (`gcloud auth login`)
- **Terraform** (>= 1.5.0) installed
- **`agents-cli`** installed:
  ```bash
  uv tool install google-agents-cli
  ```

---

## Deployment Steps

### 1. Provision Infrastructure

Run Terraform to create the required Google Cloud resources (Service Account, Secret Manager secret, Cloud Storage, BigQuery, and IAM roles):

```bash
# Preview changes (dry-run)
agents-cli infra single-project --project <PROJECT_ID>

# Apply changes
agents-cli infra single-project --apply --project <PROJECT_ID>
```

### 2. Store Secrets

Add your Google Maps API key to Secret Manager. The container automatically mounts this secret as an environment variable (`GOOGLE_MAPS_GROUNDING_LITE_API_KEY`):

```bash
echo -n "<YOUR_GOOGLE_MAPS_API_KEY>" | \
  gcloud secrets versions add google-maps-api-key \
    --project <PROJECT_ID> \
    --data-file=-
```

### 3. Deploy the Agent

Deploy the application code to Vertex AI Agent Runtime:

```bash
agents-cli deploy \
  --project <PROJECT_ID> \
  --region <REGION> \
  --service-account relocation-agent-demo-app@<PROJECT_ID>.iam.gserviceaccount.com
```

> [!TIP]
> Append `--no-wait` to deploy asynchronously in the background. You can check the progress at any time with:
> ```bash
> agents-cli deploy --status --project <PROJECT_ID>
> ```
