output "endpoint" {
  value       = local.endpoint
  description = "The endpoint and port for connecting to the proxy, of the form domain:port"
}

output "app" {
  value       = cloudfoundry_app.egress_app.id_bg
  description = "The application ID for the proxy app, useful for reference in network policies"
}