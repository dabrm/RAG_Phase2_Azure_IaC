resource "azurerm_search_service" "search" {
  name                = "rag-search-demo-mdab01"
  resource_group_name = azurerm_resource_group.rag_rg.name
  #location            = azurerm_resource_group.rag_rg.location
  location            = "eastus" #  everything sits on "eastus2", but Azure has no more search capacity available in that region.

  sku = "basic"
  
  replica_count   = 1
  partition_count = 1
}