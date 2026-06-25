## Create new EKS Cluster

```sh

# Create Cluster
eksctl create cluster -f eks-local-zone.yaml


# Get List of clusters
eksctl get cluster

# Enable IAM OIDC
eksctl utils associate-iam-oidc-provider \
    --region ap-southeast-1 \
    --cluster vietaws \
    --approve

# Replace with region & cluster name & profile (optional)
eksctl utils associate-iam-oidc-provider \
    --region ap-southeast-1 \
    --cluster vietaws \
    --approve

# check oidc on IAM - Identity provider or
aws eks describe-cluster --name vietaws --query "cluster.identity.oidc.issuer" --output text | cut -d '/' -f 5
