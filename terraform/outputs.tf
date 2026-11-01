output "openai_endpoint" {
  value = azurerm_cognitive_account.openai.endpoint
}

output "search_endpoint" {
  value = "https://${azurerm_search_service.search.name}.search.windows.net"
}

output "key_vault_url" {
  value = azurerm_key_vault.kv.vault_uri
}

output "azure_openai_chat_deployment" {
  value = azurerm_cognitive_deployment.gpt5mini.name
}

output "azure_openai_embedding_deployment" {
  value = azurerm_cognitive_deployment.embedding.name
}