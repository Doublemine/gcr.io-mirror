# k8s.gcr.io mirror

同步 gcr.io( k8s.gcr.io ) 镜像到 [dockerhub](https://hub.docker.com/r/corelab) 以供国内网络环境使用。当前同步状态:   [![Build Status](https://travis-ci.org/Doublemine/gcr.io-mirror.svg?branch=sync)](https://travis-ci.org/Doublemine/gcr.io-mirror)


# Synced Namespace

 -  [**kubernetes-helm**](kubernetes-helm.md)
 -  [**google-containers**](google-containers.md)
 -  [**cloud-solutions-images**](cloud-solutions-images.md)
 -  [**heption-images**](heption-images.md)
 -  [**k8s.gcr.io**](k8s-artifacts-prod.md)


## Usage

> You can use this script sync the namespace of gcr.io what you want.

 1. Fork this project
 2. Get Google cloud public docker images registry's cookies [gcr.io](https://console.cloud.google.com/gcr/images/google-containers) and export as env `GCR_COOKIE`
 3. Run the `sync.py -h` view more detail and add a job of Travis-CI as per namespace of gcr.io.
