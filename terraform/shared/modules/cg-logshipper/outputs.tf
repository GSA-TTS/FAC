output "username" {
  value = local.username
}

output "password" {
  value = local.password
}

output "syslog_drain_url" {
  value = local.syslog_drain
}

output "syslog_drain_name" {
  value = var.syslog_drain_name
}

output "domain" {
  value = local.domain
}

output "app_id" {
  value = local.app_id
}
