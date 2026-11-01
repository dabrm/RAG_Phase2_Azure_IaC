resource "azurerm_key_vault" "kv" {
  name                        = local.key_vault_name # local Terraform namespace (see locals.tf)
  location                    = azurerm_resource_group.rag_rg.location
  resource_group_name         = azurerm_resource_group.rag_rg.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"

  soft_delete_retention_days = 7
  purge_protection_enabled   = false
}

