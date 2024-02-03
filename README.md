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
