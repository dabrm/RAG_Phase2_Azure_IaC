terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.100"
    }
  }

  # this stores state-mgmt info in cloud, instead of locally (enterprise standard)
  backend "azurerm" {
		    resource_group_name  = "rg-terraform-state-05c07dbc"
		    storage_account_name = "tfstate05c07dbcmdab"
		    container_name       = "tfstate"
		    key                  = "rag-demo.tfstate"
  }
}

provider "azurerm" {
  features {}
}