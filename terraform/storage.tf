resource "azurerm_storage_account" "rag_storage" {
  name                     = "ragstoragedemo123"
  resource_group_name      = azurerm_resource_group.rag_rg.name
  location                 = azurerm_resource_group.rag_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}