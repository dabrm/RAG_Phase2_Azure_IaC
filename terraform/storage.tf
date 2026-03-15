resource "azurerm_storage_account" "rag_storage" {
  name                     = "ragstoragedemomdab01"
  resource_group_name      = azurerm_resource_group.rag_rg.name
  location                 = azurerm_resource_group.rag_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}