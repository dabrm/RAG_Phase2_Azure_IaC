resource "azurerm_cognitive_account" "openai" {
  name                = "rag-openai-demo"
  location            = azurerm_resource_group.rag_rg.location
  resource_group_name = azurerm_resource_group.rag_rg.name

  kind     = "OpenAI"
  sku_name = "S0"
}