resource "azurerm_key_vault_secret" "openai_endpoint" {
  name         = "openai-endpoint"
  value        = azurerm_cognitive_account.openai.endpoint
  key_vault_id = azurerm_key_vault.kv.id

  # need to explicitly define dependency, else it tries to check if secret exists (GET) before it's given acces via policy
  depends_on = [
    azurerm_key_vault_access_policy.current_user
  ]
}

resource "azurerm_key_vault_secret" "openai_key" {
  name         = "openai-api-key"
  value        = azurerm_cognitive_account.openai.primary_access_key
  key_vault_id = azurerm_key_vault.kv.id

  
  # need to explicitly define dependency, else it tries to check if secret exists (GET) before it's given acces via policy
  depends_on = [
    azurerm_key_vault_access_policy.current_user
  ]
}

resource "azurerm_key_vault_secret" "search_endpoint" {
  name         = "search-endpoint"
  #value        = azurerm_search_service.search.query_keys[0].key
  value   = "https://${azurerm_search_service.search.name}.search.windows.net"
  key_vault_id = azurerm_key_vault.kv.id

  # need to explicitly define dependency, else it tries to check if secret exists (GET) before it's given acces via policy
  depends_on = [
    azurerm_key_vault_access_policy.current_user
  ]
}

resource "azurerm_key_vault_secret" "search_key" {
  name         = "azure-search-key"
  value        = azurerm_search_service.search.primary_key
  key_vault_id = azurerm_key_vault.kv.id

  depends_on = [
    azurerm_key_vault_access_policy.current_user
  ]
}