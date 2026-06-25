## Required

- vpc-cni
- kube-proxy
- core-dns

# Create IAM Policy

```sh
# download iam policy for elb controller
curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json

# create IAM Policy on AWS

aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam_policy.json

# create IAM Service Account
eksctl create iamserviceaccount \
  --cluster=singapore-hanoi-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --role-name AmazonEKSLoadBalancerControllerRole6 \
  --attach-policy-arn=arn:aws:iam::274595021951:policy/AWSLoadBalancerControllerIAMPolicy \
  --override-existing-serviceaccounts \
  --approve

# Get IAM Service Account
eksctl  get iamserviceaccount --cluster singapore-hanoi-cluster

# Describe Service Account alb-ingress-controller
kubectl describe sa aws-load-balancer-controller -n kube-system

# Deply Egress Controller
# https://docs.aws.amazon.com/eks/latest/userguide/lbc-helm.html

helm repo add eks https://aws.github.io/eks-charts

# Update Helm chart
helm repo update

# Install

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
 -n kube-system \
 --set clusterName=singapore-hanoi-cluster \
 --set serviceAccount.create=false \
 --set serviceAccount.name=aws-load-balancer-controller

# IDMS v2 only
# addon images: https://docs.aws.amazon.com/eks/latest/userguide/add-ons-images.html
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=singapore-hanoi-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region=ap-southeast-1 \
  --set vpcId=<YOUR-VPC-ID>> \
  --set image.repository=602401143452.dkr.ecr.ap-southeast-1.amazonaws.com/amazon/aws-load-balancer-controller

# Verify
kubectl get deployment -n kube-system aws-load-balancer-controller

# Uninstall
helm delete aws-load-balancer-controller -n kube-system
```