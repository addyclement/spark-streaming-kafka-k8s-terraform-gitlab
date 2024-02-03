**Fault Tolerant Spark Streaming Pipeline - Kafka, Elastic, FluentBit, GitLab, Terraform & Kubernetes**

```
addyclement@ip-192-168-1-147 bexley-ecomm % kubectl get nodes -L eks.amazonaws.com/capacityType,eks.amazonaws.com/nodegroup
NAME                                        STATUS   ROLES    AGE   VERSION               CAPACITYTYPE   NODEGROUP
ip-10-0-79-70.eu-west-2.compute.internal    Ready    <none>   15m   v1.28.5-eks-5e0fdde   ON_DEMAND      ondemand_large-2024020319554299210000001b
ip-10-0-80-162.eu-west-2.compute.internal   Ready    <none>   14m   v1.28.5-eks-5e0fdde   SPOT           spot_large-2024020319554299580000001d

```

Project Tree Structure
```
├── bexley
│   ├── Dockerfile
│   ├── code
│   │   ├── Kafka-Producer-Code-04-MSK.py
│   │   ├── __init__.py
│   │   ├── bexley_load_auth_from_secrets_manager_v01.py
│   │   ├── bexley_spark_stream_msk_es_05.py
│   │   ├── bexley_spark_stream_msk_es_06.py
│   │   └── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── bexley_load_auth_from_secrets_manager_v01.py
│       ├── bexley_spark_stream_msk_es_04.py
│       ├── conftest.py
│       ├── data
│       ├── shipping_destinations.csv
│       ├── test_bexley_transforms.py
│       └── test_lookup_transforms.py
├── docker
│   ├── Dockerfile.Spark
│   ├── docker-compose.spark.yaml
│   └── requirements.txt
├── fluent
│   ├── elasticsearch-configmap.yaml
│   ├── elasticsearch-secret-plaindata.yaml
│   ├── elasticsearch-secret.yaml
│   ├── fluent-bit-configmap.yaml
│   ├── fluent-bit-ds.yaml
│   ├── fluent-bit-role-binding.yaml
│   ├── fluent-bit-role.yaml
│   ├── fluent-bit-service-account.yaml
│   └── namespace.yml
├── imgs
│   ├── coverage.png
│   └── demo.txt
├── spark-operator
│   ├── bexley-spark-sreaming-app.yml
│   ├── ecr_secret
│   ├── namespaces-spark.yaml
│   ├── namespaces.yaml
│   ├── pod-template-driver.yml
│   ├── pod-template-executor.yml
│   ├── spark-job4.yml
│   ├── spark-rbac-clusterbinding.yml
│   └── spark-svc-account.yaml
└── terraform
    ├── eks.tf
    ├── gitlab-ci.yaml
    ├── output.tf
    ├── provider.tf
    ├── terraform.tfvars
    ├── variables.tf
    └── vpc.tf

```
![Test Coverage](/imgs/coverage.png)


```
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
conftest.py                     6      2    67%   9-10
test_bexley_transforms.py      26     16    38%   28-123
test_lookup_transforms.py      28     18    36%   27-125
---------------------------------------------------------
TOTAL                          60     36    40%
Coverage XML written to file /builds/binaries1/bexley_ci/coverage/cobertura_coverage.xml
Required test coverage of 40% reached. Total coverage: 40.00%
=========================== short test summary info ============================
```

Deploy FluentBit Logging

```
$ aws eks update-kubeconfig --region $AWS_DEFAULT_REGION --name $EKS_CLUSTER_NAME
Added new context arn:aws:eks:[MASKED]:205232154569:cluster/bexley-on-eks to /root/.kube/config
$ curl --silent --location -o /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl
$ chmod +x /usr/local/bin/kubectl
$ echo "Create Kubernetes namespace"
Create Kubernetes namespace
$ kubectl apply -f fluent/namespace.yml
namespace/logging created
$ echo "Create secret for elastic search"
Create secret for elastic search
$ kubectl apply -f fluent/elasticsearch-secret.yaml
secret/elasticsearch-secret created
$ echo "Create Elasticsearch Config Map"
Create Elasticsearch Config Map
$ kubectl apply -f fluent/elasticsearch-configmap.yaml
configmap/elasticsearch-configmap created
$ echo "Create Service Account"
Create Service Account
$ kubectl apply -f fluent/fluent-bit-service-account.yaml
serviceaccount/fluent-bit created
$ echo "Create Cluster Role"
Create Cluster Role
$ kubectl apply -f fluent/fluent-bit-role.yaml
clusterrole.rbac.authorization.k8s.io/fluent-bit-read created
$ echo "Create Cluster Role Binding"
Create Cluster Role Binding
$ kubectl apply -f fluent/fluent-bit-role-binding.yaml
clusterrolebinding.rbac.authorization.k8s.io/fluent-bit-read created
$ echo "Create ConfigMap for Fluent bit"
Create ConfigMap for Fluent bit
$ kubectl apply -f fluent/fluent-bit-configmap.yaml
configmap/fluent-bit-config created
$ echo "Create Fluent Bit DaemonSet"
Create Fluent Bit DaemonSet
$ kubectl apply -f fluent/fluent-bit-ds.yaml
daemonset.apps/fluent-bit created
$ echo "preview assets"
preview assets
$ kubectl describe sa fluent-bit -n $LOGGING_NAMESPACE
Name:                fluent-bit
Namespace:           logging
Labels:              <none>
Annotations:         <none>
Image pull secrets:  <none>
Mountable secrets:   <none>
Tokens:              <none>
Events:              <none>
```

```
 % kubectl get pods,daemonset,configmaps,serviceaccounts -n logging           
NAME                   READY   STATUS    RESTARTS   AGE
pod/fluent-bit-hlwqk   1/1     Running   0          3m44s
pod/fluent-bit-krt69   1/1     Running   0          3m44s

NAME                        DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
daemonset.apps/fluent-bit   2         2         2       2            2           <none>          3m44s

NAME                                DATA   AGE
configmap/elasticsearch-configmap   3      3m51s
configmap/fluent-bit-config         5      3m46s
configmap/kube-root-ca.crt          1      3m54s

NAME                        SECRETS   AGE
serviceaccount/default      0         3m54s
serviceaccount/fluent-bit   0         3m50s
```
