output "backend_url" {
  value     = local.backend_url
  sensitive = true
}

output "connector_url" {
  value     = local.connector_url
  sensitive = true
}

output "frontend_url" {
  value     = local.frontend_url
  sensitive = true
}

output "backend_app_id" {
  value = local.backend_app_id
}

output "connector_app_id" {
  value = local.connector_app_id
}

output "frontend_app_id" {
  value = local.frontend_app_id
}
