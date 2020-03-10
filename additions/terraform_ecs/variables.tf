# aws_ecs_task_definition
variable "target_group_arn" {
  type        = string
  default     = ""
}
variable "execution_role_arn" {
  type        = string
  default     = ""
}
# aws_ecs_service
variable "subnets" {
  type        = list
  default     = [""]
}
variable "security_groups" {
  type        = list
  default     = [""]
}
# aws_appautoscaling_target
variable "resource_id" {
  type        = string
  default     = "service/white-hart/tabs"
}
variable "scalable_dimension" {
  type        = string
  default     = "ecs:service:DesiredCount"
}
variable "service_namespace" {
  type        = string
  default     = "ecs"
}
# aws_cloudwatch_metric_alarm
variable "ClusterName" {
  type        = string
  default     = "white-hart"
}
variable "ServiceName" {
  type        = string
  default     = "tabs"
}
