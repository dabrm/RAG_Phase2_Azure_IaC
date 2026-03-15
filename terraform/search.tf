resource "azurerm_search_service" "search" {
  name                = "rag-search-demo"
  resource_group_name = azurerm_resource_group.rag_rg.name
  location            = azurerm_resource_group.rag_rg.location

  sku = "basic"
}