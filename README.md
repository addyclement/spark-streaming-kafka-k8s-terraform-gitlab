**Fault Tolerant Spark Streaming Pipeline - Kafka, Elastic, FluentBit, GitLab, Terraform & Kubernetes**

==>> need to update producer code
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

***Deploy Spark Application to EKS***

```
$ kubectl apply -f spark-deployment/namespaces.yaml
namespace/spark-operator created
$ echo "create service account and iam role"
create service account and iam role
$ eksctl create iamserviceaccount --name $SPARK_SVC_ACC --namespace $SPARK_NAMESPACE --cluster $EKS_CLUSTER_NAME --attach-policy-arn $SVC_ACC_IAM_POLICY --approve
2024-02-04 16:36:37 [ℹ]  1 iamserviceaccount (spark-operator/spark) was included (based on the include/exclude rules)
2024-02-04 16:36:37 [!]  serviceaccounts that exist in Kubernetes will be excluded, use --override-existing-serviceaccounts to override
2024-02-04 16:36:37 [ℹ]  1 task: { 
    2 sequential sub-tasks: { 
        create IAM role for serviceaccount "spark-operator/spark",
        create serviceaccount "spark-operator/spark",
    } }2024-02-04 16:36:37 [ℹ]  building iamserviceaccount stack "eksctl-[MASKED]-addon-iamserviceaccount-spark-operator-spark"
2024-02-04 16:36:37 [ℹ]  deploying stack "eksctl-[MASKED]-addon-iamserviceaccount-spark-operator-spark"
2024-02-04 16:36:37 [ℹ]  waiting for CloudFormation stack "eksctl-[MASKED]-addon-iamserviceaccount-spark-operator-spark"
2024-02-04 16:37:08 [ℹ]  waiting for CloudFormation stack "eksctl-[MASKED]-addon-iamserviceaccount-spark-operator-spark"
2024-02-04 16:37:08 [ℹ]  created serviceaccount "spark-operator/spark"
$ echo "create role binding"
create role binding
$ kubectl apply -f spark-deployment/spark-rbac-clusterbinding.yml
clusterrolebinding.rbac.authorization.k8s.io/spark-c-role-binding created
$ echo "adding spark operator repo to helm ... "
adding spark operator repo to helm ... 
$ helm repo add spark-operator https://googlecloudplatform.github.io/spark-on-k8s-operator
"spark-operator" has been added to your repositories
$ helm install spark-operator spark-operator/spark-operator --namespace $SPARK_NAMESPACE
NAME: spark-operator
LAST DEPLOYED: Sun Feb  4 16:37:15 2024
NAMESPACE: spark-operator
STATUS: deployed
REVISION: 1
TEST SUITE: None
$ echo "creating secret for ECR registry ..."
creating secret for ECR registry ...
$ kubectl create secret docker-registry $ECR_SECRET --docker-server=$DOCKER_REGISTRY --docker-username=AWS \ # collapsed multi-line command
secret/bexley-ecr-secret created
$ echo "deploy spark application via spark operator"
deploy spark application via spark operator
$ echo "describe the iam service account"
describe the iam service account
$ kubectl describe sa $SPARK_SVC_ACC -n $SPARK_NAMESPACE
Name:                spark
Namespace:           spark-operator
Labels:              app.kubernetes.io/managed-by=eksctl
Annotations:         eks.amazonaws.com/role-arn: arn:aws:iam::205232154569:role/eksctl-[MASKED]-addon-iamserviceaccount--Role1-wOqPZy57iF8s
Image pull secrets:  <none>
Mountable secrets:   <none>
Tokens:              <none>
Events:              <none>
$ helm repo list
NAME          	URL                                                        
spark-operator	https://googlecloudplatform.github.io/spark-on-k8s-operator
$ helm list --all-namespaces
NAME          	NAMESPACE     	REVISION	UPDATED                               	STATUS  	CHART                	APP VERSION        
spark-operator	spark-operator	1       	2024-02-04 16:37:15.09944279 +0000 UTC	deployed	spark-operator-1.1.27	v1beta2-1.3.8-3.1.1
$ sleep 10
$ echo "view all resources in namepsace ..."
view all resources in namepsace ...
$ eksctl get iamserviceaccount --cluster $EKS_CLUSTER_NAME
NAMESPACE	NAME	ROLE ARN
spark-operator	spark	arn:aws:iam::205232154569:role/eksctl-[MASKED]-addon-iamserviceaccount--Role1-wOqPZy57iF8s
```
***Write Enriched Stream to Console***

```
writing enriched data set to console ...
root
 |-- window: struct (nullable = false)
 |    |-- start: timestamp (nullable = true)
 |    |-- end: timestamp (nullable = true)
 |-- fufilment_type: string (nullable = false)
 |-- total_orders: long (nullable = false)

-------------------------------------------
Batch: 0
-------------------------------------------
+------+--------------+------------+
|window|fufilment_type|total_orders|
+------+--------------+------------+
+------+--------------+------------+

-------------------------------------------
Batch: 1
-------------------------------------------
+------------------------------------------+--------------+------------+
|window                                    |fufilment_type|total_orders|
+------------------------------------------+--------------+------------+
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Merchant      |7           |
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Bexley        |3           |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Merchant      |19          |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Bexley        |4           |
+------------------------------------------+--------------+------------+

-------------------------------------------
Batch: 2
-------------------------------------------
+------------------------------------------+--------------+------------+
|window                                    |fufilment_type|total_orders|
+------------------------------------------+--------------+------------+
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Merchant      |7           |
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Bexley        |3           |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Merchant      |42          |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Bexley        |11          |
+------------------------------------------+--------------+------------+

-------------------------------------------
Batch: 3
-------------------------------------------
+------------------------------------------+--------------+------------+
|window                                    |fufilment_type|total_orders|
+------------------------------------------+--------------+------------+
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Merchant      |7           |
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Bexley        |3           |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Merchant      |66          |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Bexley        |17          |
+------------------------------------------+--------------+------------+

-------------------------------------------
Batch: 4
-------------------------------------------
+------------------------------------------+--------------+------------+
|window                                    |fufilment_type|total_orders|
+------------------------------------------+--------------+------------+
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Merchant      |7           |
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Bexley        |3           |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Merchant      |84          |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Bexley        |23          |
|{2024-02-04 18:16:00, 2024-02-04 18:18:00}|Merchant      |5           |
+------------------------------------------+--------------+------------+

-------------------------------------------
Batch: 5
-------------------------------------------
+------------------------------------------+--------------+------------+
|window                                    |fufilment_type|total_orders|
+------------------------------------------+--------------+------------+
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Merchant      |7           |
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Bexley        |3           |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Merchant      |84          |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Bexley        |23          |
|{2024-02-04 18:16:00, 2024-02-04 18:18:00}|Bexley        |7           |
|{2024-02-04 18:16:00, 2024-02-04 18:18:00}|Merchant      |30          |
+------------------------------------------+--------------+------------+

-------------------------------------------
Batch: 6
-------------------------------------------
+------------------------------------------+--------------+------------+
|window                                    |fufilment_type|total_orders|
+------------------------------------------+--------------+------------+
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Merchant      |7           |
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Bexley        |3           |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Merchant      |84          |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Bexley        |23          |
|{2024-02-04 18:16:00, 2024-02-04 18:18:00}|Bexley        |20          |
|{2024-02-04 18:16:00, 2024-02-04 18:18:00}|Merchant      |39          |
+------------------------------------------+--------------+------------+

-------------------------------------------
Batch: 7
-------------------------------------------
+------------------------------------------+--------------+------------+
|window                                    |fufilment_type|total_orders|
+------------------------------------------+--------------+------------+
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Merchant      |7           |
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Bexley        |3           |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Merchant      |84          |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Bexley        |23          |
|{2024-02-04 18:16:00, 2024-02-04 18:18:00}|Bexley        |25          |
|{2024-02-04 18:16:00, 2024-02-04 18:18:00}|Merchant      |60          |
+------------------------------------------+--------------+------------+

-------------------------------------------
Batch: 8
-------------------------------------------
+------------------------------------------+--------------+------------+
|window                                    |fufilment_type|total_orders|
+------------------------------------------+--------------+------------+
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Merchant      |7           |
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Bexley        |3           |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Merchant      |84          |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Bexley        |23          |
|{2024-02-04 18:16:00, 2024-02-04 18:18:00}|Bexley        |31          |
|{2024-02-04 18:16:00, 2024-02-04 18:18:00}|Merchant      |76          |
|{2024-02-04 18:18:00, 2024-02-04 18:20:00}|Merchant      |4           |
|{2024-02-04 18:18:00, 2024-02-04 18:20:00}|Bexley        |1           |
+------------------------------------------+--------------+------------+

-------------------------------------------
Batch: 9
-------------------------------------------
+------------------------------------------+--------------+------------+
|window                                    |fufilment_type|total_orders|
+------------------------------------------+--------------+------------+
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Merchant      |7           |
|{2024-02-04 18:12:00, 2024-02-04 18:14:00}|Bexley        |3           |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Merchant      |84          |
|{2024-02-04 18:14:00, 2024-02-04 18:16:00}|Bexley        |23          |
|{2024-02-04 18:16:00, 2024-02-04 18:18:00}|Bexley        |31          |
|{2024-02-04 18:16:00, 2024-02-04 18:18:00}|Merchant      |76          |
|{2024-02-04 18:18:00, 2024-02-04 18:20:00}|Merchant      |28          |
|{2024-02-04 18:18:00, 2024-02-04 18:20:00}|Bexley        |9           |
+------------------------------------------+--------------+------------+
```

delete infra

```
module.eks.aws_security_group.cluster[0]: Destroying... [id=sg-0be56540a26a6f6bb]
module.eks.aws_security_group.node[0]: Destroying... [id=sg-05c68102377a621f8]
module.eks.aws_security_group.cluster[0]: Destruction complete after 1s
module.eks.aws_security_group.node[0]: Destruction complete after 1s
module.vpc.aws_vpc.this[0]: Destroying... [id=vpc-0a8e7f2a799843186]
module.vpc.aws_vpc.this[0]: Destruction complete after 1s
╷
│ Warning: EC2 Default Network ACL (acl-0f4fbd44e8491c1d1) not deleted, removing from state
│ 
│ 
╵
Releasing state lock. This may take a few moments...
Destroy complete! Resources: 72 destroyed.
Saving cache for successful job
00:14
Creating cache default-protected...
.terraform: found 417 matching artifact files and directories 
Uploading cache.zip to https://storage.googleapis.com/gitlab-com-runners-cache/project/54093755/default-protected 
Created cache
Cleaning up project directory and file based variables
00:00
Job succeeded
```
