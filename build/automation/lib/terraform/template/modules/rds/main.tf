module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "2.20.0"
  tags    = var.context.tags

  # DB Instance

  identifier = var.db_instance
  port       = var.db_port
  name       = var.db_name
  username   = var.db_username
  password   = var.db_password

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  engine                = "postgres"
  engine_version        = "AWS_POSTGRES_VERSION_TEMPLATE_TO_REPLACE"
  instance_class        = var.db_instance_class
  storage_encrypted     = true

  allow_major_version_upgrade  = false
  apply_immediately            = true
  backup_retention_period      = var.db_backup_retention_period
  backup_window                = "00:00-01:00"
  copy_tags_to_snapshot        = true
  final_snapshot_identifier    = var.db_instance
  maintenance_window           = "Mon:05:00-Mon:06:00"
  multi_az                     = var.db_multi_az
  performance_insights_enabled = true
  skip_final_snapshot          = var.db_skip_final_snapshot

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  monitoring_interval             = "30"
  monitoring_role_arn             = aws_iam_role.rds_enhanced_monitoring.arn

  vpc_security_group_ids = [aws_security_group.security_group.id]
  subnet_ids             = var.subnet_ids

  # DB Parameter Group

  family = "postgres${AWS_POSTGRES_VERSION_MAJOR_TEMPLATE_TO_REPLACE}"
  parameters = [
    {
      name         = "max_connections"
      value        = var.db_max_connections
      apply_method = "pending-reboot"
    },
    {
      name         = "client_encoding"
      value        = "UTF8"
      apply_method = "immediate"
    },
    {
      name         = "ssl"
      value        = "1"
      apply_method = "immediate"
    },
    {
      name         = "rds.force_ssl"
      value        = "1"
      apply_method = "immediate"
    },
    {
      name         = "timezone"
      value        = "UTC"
      apply_method = "immediate"
    }
  ]

  # DB Option Group

  major_engine_version = "AWS_POSTGRES_VERSION_MAJOR_TEMPLATE_TO_REPLACE"
  options = [
  ]
}

### Networking #################################################################

resource "aws_security_group" "security_group" {
  name        = "${var.db_instance}-rds-sg"
  vpc_id      = var.vpc_id
  tags        = var.context.tags
  description = "Allow incoming connections to the RDS PostgreSQL instance from the specified VPC"
}

resource "aws_security_group_rule" "ingress" {
  for_each                 = { for id in var.security_group_ids : id => id }
  type                     = "ingress"
  from_port                = var.db_port
  to_port                  = var.db_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.security_group.id
  source_security_group_id = each.value
  description              = "A rule to allow incoming connections to the RDS PostgreSQL instance from the specified Security Groups"
}

### IAM role for enhanced monitoring ###########################################

resource "aws_iam_role" "rds_enhanced_monitoring" {
  name_prefix        = "rds-enhanced-monitoring-"
  assume_role_policy = data.aws_iam_policy_document.rds_enhanced_monitoring.json
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  role       = aws_iam_role.rds_enhanced_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

data "aws_iam_policy_document" "rds_enhanced_monitoring" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["monitoring.rds.amazonaws.com"]
    }
  }
}
