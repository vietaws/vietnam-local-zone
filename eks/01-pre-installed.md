## Install aws pre-requisites

- aws cli

    - https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

    - https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html

- configure aws credentials for cli


```sh
# macOs

curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# verify
which aws

# version
aws --version
```

## Install eksctl & kubectl cli

Guide: https://eksctl.io/installation/

```sh
# for ARM systems, set ARCH to: `arm64`, `armv6` or `armv7`
ARCH=amd64
PLATFORM=windows_$ARCH

curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.zip"

# (Optional) Verify checksum
curl -sL "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_checksums.txt" | grep $PLATFORM | sha256sum --check

unzip eksctl_$PLATFORM.zip -d $HOME/bin

rm eksctl_$PLATFORM.zip

# verify
eksctl info

kubectl version
```