terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.100"
    }
  }

  # this stores state-mgmt info in cloud, instead of locally (enterprise standard)
  backend "azurerm" {
		    resource_group_name  = "rg-terraform-state"
		    storage_account_name = "tfstateragdemo123"
		    container_name       = "tfstate"
		    key                  = "rag-demo.tfstate"
  }
}

provider "azurerm" {
  features {}
}