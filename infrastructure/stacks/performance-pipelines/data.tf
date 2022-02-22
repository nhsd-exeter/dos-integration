data "template_file" "stress_tests_buildspec" {
  template = file("stress-test-buildspec.yml")
}

data "template_file" "load_tests_buildspec" {
  template = file("load-test-buildspec.yml")
}

data "aws_kms_key" "signing_key" {
  key_id = "alias/${var.signing_key_alias}"
}
