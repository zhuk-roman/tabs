#terraform graph | dot –Tpng > graph.png
# "LoadBalancerArn": "arn:aws:elasticloadbalancing:eu-central-1:146080453141:loadbalancer/app/tabslb/131293931049c1b4"
# "TargetGroupArn": "arn:aws:elasticloadbalancing:eu-central-1:146080453141:targetgroup/ecs-fargat-tabs/9b79d307564b00aa"

provider "aws" {
  profile = "default"
  region  = "eu-central-1"
}

resource "aws_ecs_cluster" "cluster" {
  name = "white-hart"
}

resource "aws_ecs_task_definition" "tabs" {
  family                   = "tabs"
  container_definitions    = file("task-definitions/tabs.json")
  execution_role_arn       = var.execution_role_arn
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  # https://docs.aws.amazon.com/cli/latest/reference/ecs/register-task-definition.html
  cpu    = 256
  memory = 512

  depends_on = [aws_ecs_cluster.cluster]
}

# resource "aws_ecs_task_definition" "tabs_ec2" {
#   family                = "tabs_ec2"
#   container_definitions = "${file("task-definitions/tabs.json")}"

#   requires_compatibilities = ["EC2"]
#   network_mode = "bridge"
#   execution_role_arn = var.execution_role_arn
# }

resource "aws_ecs_service" "tabs" {
  name            = "tabs"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.tabs.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = var.subnets
    security_groups  = var.security_groups
    assign_public_ip = true
  }
  depends_on = [aws_ecs_cluster.cluster]
  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "tabs"
    container_port   = 80
  }
  lifecycle {
    ignore_changes = [desired_count]
  }
}

resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity = 20
  min_capacity = 1
  resource_id  = var.resource_id
  scalable_dimension = var.scalable_dimension
  service_namespace  = var.service_namespace
  depends_on         = [aws_ecs_service.tabs]
}

resource "aws_appautoscaling_policy" "ecs_service_scale_down" {
  name               = "scale-down"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 60
    metric_aggregation_type = "Maximum"

    step_adjustment {
      metric_interval_upper_bound = 0
      scaling_adjustment          = -3
    }
  }
  depends_on = [aws_appautoscaling_target.ecs_target]
}

resource "aws_appautoscaling_policy" "ecs_service_scale_up" {
  name               = "scale-up"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 60
    metric_aggregation_type = "Maximum"

    step_adjustment {
      metric_interval_lower_bound = 0
      scaling_adjustment          = 4
    }
  }
  depends_on = [aws_appautoscaling_target.ecs_target]
}

resource "aws_cloudwatch_metric_alarm" "service_cpu_scale_down" {
  alarm_name          = "ServiceCPUScaleDown"
  comparison_operator = "LessThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "Average"
  threshold           = "20"

  dimensions = {
    ClusterName = var.ClusterName
    ServiceName = var.ServiceName
  }

  alarm_description = "ECS cpu scale down"
  alarm_actions     = [aws_appautoscaling_policy.ecs_service_scale_down.arn]
}

resource "aws_cloudwatch_metric_alarm" "service_cpu_scale_up" {
  alarm_name          = "ServiceCPUScaleUp"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "Average"
  threshold           = "50"

  dimensions = {
    ClusterName = var.ClusterName
    ServiceName = var.ServiceName
  }

  alarm_description = "ECS cpu scale down"
  alarm_actions     = [aws_appautoscaling_policy.ecs_service_scale_up.arn]
}
