resource "aws_s3_bucket" "b" {
  bucket = "test-bucket"
  tags = {
    Name        = "bucket"
    Environment = "dev"
  }
}

resource "aws_s3_bucket_acl" "acl" {
  bucket = aws_s3_bucket.b.id
  acl    = "private"
}
