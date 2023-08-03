resource "aws_wafv2_web_acl" "di_endpoint_waf" {
  #checkov:skip=CKV_AWS_192
  name        = var.waf_acl_name
  description = "WAF ACL for the DoS Integration API Gateway"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = var.waf_ip_allow_list_rule_name
    priority = 1

    action {
      count {}
    }

    statement {
      not_statement {
        statement {
          ip_set_reference_statement {
            arn = aws_wafv2_ip_set.di_endpoint_ip_set.arn
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = var.waf_ip_allow_list_metric_name
      sampled_requests_enabled   = true
    }
  }

  rule {
    name = var.waf_rate_based_rule_name
    action {
      count {}
    }
    priority = 2

    statement {
      rate_based_statement {
        limit = 150000 # 500 requests per second
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = var.waf_rate_based_metric_name
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = var.waf_aws_common_rule_name
    priority = 3

    override_action {
      count {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = var.waf_aws_common_metric_name
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = var.waf_non_gb_rule_name
    priority = 4
    action {
      count {}
    }
    statement {
      not_statement {
        statement {
          geo_match_statement {
            country_codes = ["GB"]
          }
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = var.non_gb_rule_metric_name
      sampled_requests_enabled   = true
    }
  }



  rule {
    name     = var.waf_aws_known_bad_inputs_rule_name
    priority = 5

    override_action {
      count {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = var.waf_aws_known_bad_inputs_metric_name
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = var.waf_aws_sqli_rule_name
    priority = 6

    override_action {
      count {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = var.waf_aws_sqli_metric_name
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = var.waf_ip_reputation_list_rule_name
    priority = 7

    override_action {
      count {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = var.ip_reputation_list_metric_name
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = var.waf_acl_metric_name
    sampled_requests_enabled   = true
  }

  depends_on = [
    aws_wafv2_ip_set.di_endpoint_ip_set
  ]
}

resource "aws_wafv2_ip_set" "di_endpoint_ip_set" {
  name               = var.waf_ip_set_name
  description        = "IP set for the DoS Integration API Gateway"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"
  addresses          = toset(local.ip_addresses)
}

resource "aws_wafv2_web_acl_logging_configuration" "waf_acl_lc" {
  log_destination_configs = [aws_cloudwatch_log_group.waf_logs.arn]
  resource_arn            = aws_wafv2_web_acl.di_endpoint_waf.arn
}

resource "aws_wafv2_web_acl_association" "di_endpoint_waf_association" {
  resource_arn = aws_api_gateway_stage.di_endpoint_stage.arn
  web_acl_arn  = aws_wafv2_web_acl.di_endpoint_waf.arn

  depends_on = [
    aws_api_gateway_stage.di_endpoint_stage,
    aws_wafv2_web_acl.di_endpoint_waf
  ]

}
