**Fault Tolerant Spark Streaming Pipeline - Kafka, Elastic, FluentBit, GitLab, Terraform & Kubernetes**

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
