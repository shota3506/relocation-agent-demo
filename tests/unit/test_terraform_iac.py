from pathlib import Path


def test_minimal_terraform_infrastructure_files_exist():
    """Verify that minimal Terraform IaC configuration files exist and are well-structured."""
    base = Path(__file__).parent.parent.parent / "deployment" / "terraform"
    assert (base / "main.tf").exists()
    assert (base / "variables.tf").exists()
    assert (base / "outputs.tf").exists()
    assert (base / "terraform.tfvars.example").exists()

    # Verify main.tf content covers essential resources
    main_content = (base / "main.tf").read_text(encoding="utf-8")
    assert "aiplatform.googleapis.com" in main_content
    assert "cloudtrace.googleapis.com" in main_content
    assert "dlp.googleapis.com" in main_content
    assert "google_service_account" in main_content
    assert "roles/aiplatform.user" in main_content
    assert "google_storage_bucket" in main_content
