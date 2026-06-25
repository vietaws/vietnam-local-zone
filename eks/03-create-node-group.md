```sh
# Manual Create Hanoi Local Zone Subnet
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:alpha.eksctl.io/cluster-name,Values=	
singapore-hanoi-cluster" --query "Vpcs[].VpcId" --output text --region ap-southeast-1)

# Create subnet
SUBNET_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.160.0/20 --availability-zone ap-southeast-1-han-1a --query "Subnet.SubnetId" --output text --region ap-southeast-1)

# Tagging eks subnet
aws ec2 create-tags --resources $SUBNET_ID --tags Key=kubernetes.io/cluster/singapore-hanoi-cluster,Value=shared --region ap-southeast-1

# Create Node Group
# ✅ TODO: Update the subnet id to manifest
eksctl create nodegroup -f hanoi-nodes.yaml
``