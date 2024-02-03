module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  cluster_endpoint_private_access = var.cluster_endpoint_private_access
  cluster_endpoint_public_access  = var.cluster_endpoint_public_access

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  enable_irsa = var.enable_irsa

  cluster_enabled_log_types = ["api","scheduler"]


  cluster_addons = {
    coredns = {
      most_recent = true

      resolve_conflicts_on_create = "OVERWRITE"
      resolve_conflicts_on_update = "OVERWRITE"
      
    }
    kube-proxy = {
      most_recent = true

      resolve_conflicts_on_create = "OVERWRITE"
      resolve_conflicts_on_update = "OVERWRITE"
      
    }
    vpc-cni = {
      most_recent = true

      resolve_conflicts_on_create = "OVERWRITE"
      resolve_conflicts_on_update = "OVERWRITE"
    }
  }

  eks_managed_node_group_defaults = {
    disk_size = 25
  }

  eks_managed_node_groups = {
    ondemand_small = {
      node_group_name = "mng-ondemand-small-instance"
      desired_size = 1
      min_size     = 1
      max_size     = 3

      labels = {
        role = "driver-node"
      }

      instance_types = ["t3.small", "t3a.small"]
      capacity_type  = "ON_DEMAND"
    },

    spot_small = {
      node_group_name = "mng-spot-small-instance"
      capacity_type   = "SPOT"
      instance_types  = ["t3.small", "t3a.small"]
      max_size        = 3
      desired_size    = 1
      min_size        = 1

      subnet_ids = module.vpc.private_subnets

      taints = {
        spotInstance = {
          key    = "spotInstance"
          value  = "true"
          effect = "PREFER_NO_SCHEDULE"
        }
      }

      # iam:
      # attachPolicyARNs:
      # - arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy
      # - arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
      # - arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy
      # - <<Policy ARN>>

      labels = {
        intent = "executor-nodes"
      }
    }
  }

  # manage_aws_auth_configmap = true
  # aws_auth_roles = [
  #   {
  #     rolearn  = module.eks_terraform_admin_iam_assumable_role.iam_role_arn
  #     username = module.eks_terraform_admin_iam_assumable_role.iam_role_name
  #     groups   = ["system:masters"]
  #   },
  # ]

  tags = var.eks_tags
}