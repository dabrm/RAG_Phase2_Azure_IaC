resource "azurerm_key_vault" "kv" {
  name                        = local.key_vault_name # local Terraform namespace (see locals.tf)
  location                    = azurerm_resource_group.rag_rg.location
  resource_group_name         = azurerm_resource_group.rag_rg.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"

  soft_delete_retention_days = 7
  purge_protection_enabled   = false
}

# indexes names - also stored as KV secrets (to make it easier for future deployments)
resource "azurerm_key_vault_secret" "search_index_name" {
  name         = "search-index-name"
  value        = local.search_index_name
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "search_ingestion_index_name" {
  name         = "search-ingestion-index-name"
  value        = local.search_ingestion_index_name
  key_vault_id = azurerm_key_vault.kv.id
}
