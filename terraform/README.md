# Terraform Infrastructure

## Quick Start (Docker - Local Development)

The Docker provider is configured for local development and testing:

```bash
cd terraform
terraform init
terraform plan -var="provider_type=docker" -var-file=envs/dev/terraform.tfvars
terraform apply -var="provider_type=docker" -var-file=envs/dev/terraform.tfvars
```

## Cloud Deployment

For cloud deployments (AWS, GCP, Azure), you need to:

1. Configure cloud provider credentials
2. Use the appropriate module
3. Update terraform.tfvars with cloud-specific settings

### AWS Example

```bash
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

cd terraform
terraform init
terraform plan -var="provider_type=aws" -var-file=envs/prod/terraform.tfvars
terraform apply -var="provider_type=aws" -var-file=envs/prod/terraform.tfvars
```

## Note

Due to Terraform limitations with dynamic module selection, the current configuration
deploys all modules conditionally. Only the module matching your `provider_type`
variable will be active.

For production use, it's recommended to:
1. Create separate directories for each provider
2. Or use Terraform workspaces with provider-specific configurations
