# S3 LOG BUCKET
# S3 LOG BUCKET
# S3 LOG BUCKET
resource "aws_s3_bucket" "log_bucket" {
  bucket = var.s3_log_bucket_name
  # acl    = "log-delivery-write"
}

resource "aws_s3_bucket_public_access_block" "log_bucket_pub_acc_block" {
  bucket = aws_s3_bucket.log_bucket.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
