from pathlib import Path


def test_minimal_terraform_infrastructure_files_exist():
    """Verify that Terraform IaC configuration files exist in single-project and are well-structured."""
    base = (
        Path(__file__).parent.parent.parent
        / "deployment"
        / "terraform"
        / "single-project"
    )
    assert (base / "apis.tf").exists()
    assert (base / "iam.tf").exists()
    assert (base / "service.tf").exists()
    assert (base / "secrets.tf").exists()
    assert (base / "storage.tf").exists()
    assert (base / "variables.tf").exists()
    assert (base / "outputs.tf").exists()

    # Verify content across tf files covers essential resources
    all_tf_content = "\n".join(p.read_text(encoding="utf-8") for p in base.glob("*.tf"))
    assert "aiplatform.googleapis.com" in all_tf_content
    assert "cloudtrace.googleapis.com" in all_tf_content
    assert "dlp.googleapis.com" in all_tf_content
    assert "bigqueryconnection.googleapis.com" in all_tf_content
    assert "secretmanager.googleapis.com" in all_tf_content
    assert "google-maps-api-key" in all_tf_content
    assert "google_service_account" in all_tf_content
    assert "roles/aiplatform.user" in all_tf_content
    assert "roles/dlp.user" in all_tf_content
    assert "roles/secretmanager.secretAccessor" in all_tf_content
    assert "google_storage_bucket" in all_tf_content
