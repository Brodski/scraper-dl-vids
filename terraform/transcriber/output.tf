output "path_module" {
  value       = "${path.module}/output_code.zip"
}
output "ouput_lambda_zip" {
  value       = data.archive_file.lambda_zip.output_path
}
output "my_sense_vars" {
  value = var.sensitive_info
}