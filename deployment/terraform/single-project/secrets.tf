# Secret resource for Google Maps API Key
# Security Note: The secret value (payload) is intentionally NOT managed in Terraform
# to avoid committing secrets to version control or exposing them in terraform.tfstate.
resource "google_secret_manager_secret" "google_maps_api_key" {
  secret_id = "google-maps-api-key"
  project   = var.project_id

  replication {
    auto {}
  }

  depends_on = [google_project_service.services]
}

# Grant Secret Accessor to Agent Application Service Account
resource "google_secret_manager_secret_iam_member" "app_sa_maps_key_accessor" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.google_maps_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app_sa.email}"
}

# Grant Secret Accessor to Vertex AI Service Agent
resource "google_secret_manager_secret_iam_member" "vertex_sa_maps_key_accessor" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.google_maps_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = google_project_service_identity.vertex_sa.member
}
