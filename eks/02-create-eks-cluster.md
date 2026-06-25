## Create new EKS Cluster

```sh
# Get List of clusters
eksctl get cluster

# Create Cluster
eksctl create cluster -f cluster.yaml

# Get List of clusters
eksctl get cluster

# Enable IAM OIDC
eksctl utils associate-iam-oidc-provider \
    --region ap-southeast-1 \
    --cluster singapore-hanoi-cluster \
    --approve

# Replace with region & cluster name & profile (optional)
eksctl utils associate-iam-oidc-provider \
    --region ap-southeast-1 \
    --cluster singapore-hanoi-cluster \
    --approve

# check oidc on IAM - Identity provider or
aws eks describe-cluster --name singapore-hanoi-cluster --query "cluster.identity.oidc.issuer" --output text | cut -d '/' -f 5
