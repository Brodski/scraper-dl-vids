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




# S3 ASSETS
# S3 ASSETS
# S3 ASSETS
# S3 ASSETS
resource "aws_s3_bucket" "s3_test_assets_bucket" {
  bucket = var.s3_asset_bucket_name
  # acl    = "public-read"
  logging {
    target_bucket = aws_s3_bucket.log_bucket.bucket
    target_prefix = "logs-asset-bucket/"
  }
}

resource "aws_s3_bucket_policy" "s3test_policy" {
  bucket = aws_s3_bucket.s3_test_assets_bucket.bucket

  policy = jsonencode({
    "Version": "2008-10-17",
    Id      = "MYBUCKETPOLICY"
    "Statement": [
        {
            "Sid": "AllowPublicRead",
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Action": "S3:GetObject",
            "Resource": "arn:aws:s3:::s3-dev-assets-1213e144-b60d/*"
        }
    ]
  })
}
resource "aws_s3_bucket_public_access_block" "s3_test_assets_bucket_pub_acc_block" {
  bucket = aws_s3_bucket.s3_test_assets_bucket.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

output "log_bucket" {
  value = "${aws_s3_bucket.log_bucket.bucket_domain_name}"
}