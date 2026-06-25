## Create Node Group

```sh
# Create Public Node Group
eksctl create nodegroup --cluster=vietaws \
                       --region=ap-southeast-1 \
                       --name=public-ng1 \
                       --node-type=c7i.large \
                       --nodes=1 \
                       --nodes-min=1 \
                       --nodes-max=3 \
                       --node-volume-size=20 \
                       --managed \
                       --asg-access \
                       --external-dns-access \
                       --full-ecr-access \
                       --appmesh-access \
                       --alb-ingress-access

# Create Private node group
eksctl create nodegroup --cluster=vietaws \
                        --region=ap-southeast-1 \
                        --name=private-ng1 \
                        --node-type=c7i.large \
                        --nodes-min=2 \
                        --nodes-max=4 \
                        --node-volume-size=20 \
                        --managed \
                        --asg-access \
                        --external-dns-access \
                        --full-ecr-access \
                        --appmesh-access \
                        --alb-ingress-access \
                        --node-private-networking

# Verify
eksctl get nodegroup --cluster=vietaws

# Delete Node Group
eksctl delete nodegroup private-ng1 --cluster vietaws
```