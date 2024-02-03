### Cluster ##
cluster_name = "bexley-on-eks"
cluster_endpoint_private_access = true
cluster_endpoint_public_access  = true
cluster_version = "1.28"

#### VPC ###
vpc_name = "bexley-vpc"
enable_nat_gateway = true
enable_vpn_gateway = true

#karpenter
karpenter_chart_version = "v0.30.0"