# AWS Infrastructure for AI DevOps
# This module provisions an EKS cluster with monitoring for AI workloads

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "ai-devops"
      ManagedBy   = "terraform"
    }
  }
}

# VPC Module
module "vpc" {
  source = "./vpc"

  environment         = var.environment
  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  private_subnet_cidr = var.private_subnet_cidr
  public_subnet_cidr  = var.public_subnet_cidr
}

# EKS Module
module "eks" {
  source = "./eks"

  environment        = var.environment
  cluster_name       = var.cluster_name
  cluster_version    = var.cluster_version
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  node_groups        = var.node_groups
}

# IAM Module
module "iam" {
  source = "./iam"

  environment  = var.environment
  cluster_name = var.cluster_name
  eks_oidc_provider_arn = module.eks.oidc_provider_arn
}

# CloudWatch Module
module "cloudwatch" {
  source = "./cloudwatch"

  environment       = var.environment
  cluster_name      = var.cluster_name
  log_retention_days = var.log_retention_days
  enable_container_insights = var.enable_container_insights
}
