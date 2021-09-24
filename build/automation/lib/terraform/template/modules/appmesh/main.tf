resource "aws_appmesh_mesh" "appmesh" {
  tags = var.context.tags

  name = var.name
  spec {
    egress_filter {
      type = "ALLOW_ALL"
    }
  }
}
