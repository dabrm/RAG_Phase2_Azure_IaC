# pulling subscription-level names to use them in resource naming logic
# this way, for next subscription deployment, we won't have to manually update names that need to be globally-unique (storage-acc, key-vaults etc)

data "azurerm_client_config" "current" {}

locals {
  # Deterministic identifier based on the current Azure subscription
  subscription_suffix = substr(
    sha256(data.azurerm_client_config.current.subscription_id),
    0,
    8
  )

# Globally unique resource names
key_vault_name = "rag-kv-demo-${local.subscription_suffix}"
search_name    = "rag-search-demo-${local.subscription_suffix}"

# Storage accounts: lowercase alphanumeric only, max 24 characters
storage_account_name = "ragstoragedemo${local.subscription_suffix}"

# Cognitive Services account
openai_name = "rag-openai-demo-${local.subscription_suffix}"



# Azure AI Search index names
search_index_name           = "rag-documents-${local.subscription_suffix}"
search_ingestion_index_name = "rag-ingestion-tracking-${local.subscription_suffix}"
}
