output "database_uri" {
  value       = aiven_pg.bd_tse.service_uri
  sensitive   = true
  description = "URI de conexão ao banco PostgreSQL"
}