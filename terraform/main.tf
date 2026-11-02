terraform {
  required_providers {
    aiven = {
      source  = "aiven/aiven"
      version = ">= 4.0.0"
    }
  }
}

provider "aiven" {
  api_token = var.aiven_api_token
}

resource "aiven_pg" "bd_tse" {
  project                 = "ucsal-7da8"
  cloud_name              = "google-southamerica-east1"
  plan                    = "hobbyist"
  service_name            = "tse-representatividade-pg"
}