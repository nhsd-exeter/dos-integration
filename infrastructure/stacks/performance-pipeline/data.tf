data "template_file" "performance_tests_buildspec" {
  template = file("performance-buildspec.yml")
}
