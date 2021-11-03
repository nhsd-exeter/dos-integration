data "template_file" "unit_tests_buildspec" {
  template = file("unit-tests-buildspec.yml")
}

data "template_file" "build_and_deploy_buildspec" {
  template = file("build-and-deploy-buildspec.yml")
}

data "template_file" "e2e_test_buildspec" {
  template = file("e2e-test-buildspec.yml")
}
