**Fault Tolerant Spark Streaming Pipeline - Kafka, Elastic, FluentBit, GitLab, Terraform & Kubernetes**

==>> need to update producer code
```
% kubectl get nodes -L eks.amazonaws.com/capacityType,eks.amazonaws.com/nodegroup
NAME                                        STATUS   ROLES    AGE     VERSION               CAPACITYTYPE   NODEGROUP
ip-10-0-62-169.eu-west-2.compute.internal   Ready    <none>   6h49m   v1.28.5-eks-5e0fdde   SPOT           spot_large-2024020415473218410000001b
ip-10-0-68-223.eu-west-2.compute.internal   Ready    <none>   6h49m   v1.28.5-eks-5e0fdde   ON_DEMAND      ondemand_large-2024020415473218570000001d

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


Gitlab Image Build 

![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/be72e198-0382-40b3-a1d4-9879c0aa793b)


![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/212ce511-57bb-4468-863f-df9e081b9034)


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

![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/9dd69359-251b-43ec-ad02-c24d4418819c)


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
View FluentBit Logs in Elastic

![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/c8128523-a918-4a65-8956-1637b4e8ca68)

Run Producer code
```
{
  "freight": 17,
  "order_id": 3822,
  "customer_id": 86278,
  "ship_method": "Overnight",
  "order_date": "2024-02-04T21:36:30.306375",
  "order_total": 357,
  "order_basket": [
    {
      "order_qty": 1,
      "product_id": 13558,
      "is_discounted": false
    },
    {
      "order_qty": 7,
      "product_id": 9549,
      "is_discounted": true
    },
    {
      "order_qty": 3,
      "product_id": 11012,
      "is_discounted": false
    }
  ],
  "order_number": "1256-3077-7558",
  "ship_to_city_id": 27,
  "discount_applied": 6
}
```

***Deploy Spark Application to EKS***

![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/c4ba5bc7-6f12-4fee-bc3b-7a4336b1f29b)


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

```
% kubectl apply -f bexley-spark-sreaming-app.yml
sparkapplication.sparkoperator.k8s.io/bexley-spark-streaming-svc created

% kubectl get pods -A
NAMESPACE        NAME                                READY   STATUS              RESTARTS   AGE
kube-system      aws-node-gr5zb                      2/2     Running             0          172m
kube-system      aws-node-rwk9m                      2/2     Running             0          172m
kube-system      coredns-798c569cc7-q7h6c            1/1     Running             0          172m
kube-system      coredns-798c569cc7-wpqzt            1/1     Running             0          172m
kube-system      kube-proxy-gq2j7                    1/1     Running             0          172m
kube-system      kube-proxy-hl557                    1/1     Running             0          172m
logging          fluent-bit-8j9xb                    1/1     Running             0          143m
logging          fluent-bit-8wrlk                    1/1     Running             0          143m
spark-operator   bexley-spark-streaming-svc-driver   0/1     ContainerCreating   0          7s
spark-operator   spark-operator-675d97df85-4sqd5     1/1     Running             0          125m

kubectl get pods -A                                                 
NAMESPACE        NAME                                READY   STATUS    RESTARTS   AGE
kube-system      aws-node-gr5zb                      2/2     Running   0          3h12m
kube-system      aws-node-rwk9m                      2/2     Running   0          3h12m
kube-system      coredns-798c569cc7-q7h6c            1/1     Running   0          3h12m
kube-system      coredns-798c569cc7-wpqzt            1/1     Running   0          3h12m
kube-system      kube-proxy-gq2j7                    1/1     Running   0          3h12m
kube-system      kube-proxy-hl557                    1/1     Running   0          3h12m
logging          fluent-bit-8j9xb                    1/1     Running   0          163m
logging          fluent-bit-8wrlk                    1/1     Running   0          163m
spark-operator   bexley-spark-streaming-svc-driver   1/1     Running   0          71s
spark-operator   spark-operator-675d97df85-4sqd5     1/1     Running   0          145m

```

![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/333bf741-5c5b-47c3-ba09-f2edaeaaa64f)


Pods View
![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/89afec13-b252-4be1-aca8-418c6c045f3a)

Config
![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/3dbe9305-bcb6-4403-8116-1839b17fd518)


node 2 overview

![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/651b92e5-cbbb-4ade-8f3e-f0dbadc4df5f)

```
kubectl logs  -f pod/bexley-spark-streaming-svc-driver -n spark-operator
exploded schema of the data frame
root
 |-- order_id: integer (nullable = true)
 |-- order_total: double (nullable = true)
 |-- ship_to_city_id: integer (nullable = true)
 |-- freight: double (nullable = true)
 |-- customer_id: integer (nullable = true)
 |-- ship_method: string (nullable = true)
 |-- order_number: string (nullable = true)
 |-- discount_applied: double (nullable = true)
 |-- order_date: string (nullable = true)
 |-- order_basket: array (nullable = true)
 |    |-- element: struct (containsNull = true)
 |    |    |-- order_qty: integer (nullable = true)
 |    |    |-- product_id: integer (nullable = true)
 |    |    |-- is_discounted: boolean (nullable = true)
 |-- basket_exp: struct (nullable = true)
 |    |-- order_qty: integer (nullable = true)
 |    |-- product_id: integer (nullable = true)
 |    |-- is_discounted: boolean (nullable = true)
 |-- product_id: integer (nullable = true)
 |-- order_qty: integer (nullable = true)

Select specific colums from the data frame, transforming alongside
printing out the schema for the transformed kafka feed
root
 |-- order_number: string (nullable = true)
 |-- discounted_total: double (nullable = true)
 |-- data_key: string (nullable = false)
 |-- ship_to_city_id: integer (nullable = true)
 |-- order_date: string (nullable = true)
 |-- ship_method: string (nullable = true)
 |-- fufilment_type: string (nullable = false)

Initial Transformation of Raw Kafka Stream Successful ...
{"@timestamp":"2024-02-04T19:02:04.302Z","log.level":"info","message":"JSON Dataframe Transformed","ecs":{"version":"1.6.0"},"http":{"request":{"body":{"content":"JSON Dataframe Transformed"}}},"log":{"logger":"__main__","origin":{"file":{"line":411,"name":"bexley_spark_stream_msk_es_05.py"},"function":"transform_json_message"},"original":"JSON Dataframe Transformed"},"process":{"name":"MainProcess","pid":81,"thread":{"id":139940811222848,"name":"MainThread"}}}
writing enriched data set to console ...
-------------------------------------------
Batch: 0
-------------------------------------------
+--------------+-----------------+-------------------------+---------------+--------------------------+-----------------+--------------+
|order_number  |discounted_total |data_key                 |ship_to_city_id|order_date                |ship_method      |fufilment_type|
+--------------+-----------------+-------------------------+---------------+--------------------------+-----------------+--------------+
|1945-3274-7556|890.01           |1945-3274-7556-2024-01-30|44             |2024-01-30T15:50:02.879982|Same-day delivery|Bexley        |
|5837-5611-6373|497.7            |5837-5611-6373-2024-01-30|49             |2024-01-30T15:50:04.415186|Flat rate        |Merchant      |
|2011-5421-6634|674.1            |2011-5421-6634-2024-01-30|55             |2024-01-30T15:50:04.946595|Same-day delivery|Merchant      |
|6149-3789-5975|563.5699999999999|6149-3789-5975-2024-01-30|35             |2024-01-30T15:50:05.869356|Expedited        |Bexley        |
|6427-6882-5012|59.4             |6427-6882-5012-2024-01-30|60             |2024-01-30T15:50:06.790050|Overnight        |Merchant      |
|1733-5784-9865|374.64           |1733-5784-9865-2024-01-30|61             |2024-01-30T15:50:07.978531|Freight          |Merchant      |
|4615-3525-8973|1113.6           |4615-3525-8973-2024-01-30|18             |2024-01-30T15:50:08.549629|Same-day delivery|Bexley        |
|6070-4937-5799|549.9            |6070-4937-5799-2024-01-30|41             |2024-01-30T15:50:09.708694|Freight          |Merchant      |
|4634-4194-5365|1029.6           |4634-4194-5365-2024-01-30|5              |2024-01-30T15:50:10.581634|2-day shipping   |Merchant      |
|4250-3730-9480|97.68            |4250-3730-9480-2024-01-30|24             |2024-01-30T15:50:12.015131|International    |Bexley        |
|4328-3618-5500|835.58           |4328-3618-5500-2024-01-30|43             |2024-01-30T15:50:13.155637|Freight          |Bexley        |
|8196-5427-9916|1046.22          |8196-5427-9916-2024-01-30|18             |2024-01-30T15:50:14.051313|Overnight        |Merchant      |
|2939-5909-8275|990.99           |2939-5909-8275-2024-01-30|38             |2024-01-30T15:50:15.564162|Freight          |Merchant      |
|6578-6786-7564|926.52           |6578-6786-7564-2024-01-30|25             |2024-01-30T15:50:17.039149|Same-day delivery|Merchant      |
|1683-6586-7592|945.2            |1683-6586-7592-2024-01-30|4              |2024-01-30T15:50:17.597214|Expedited        |Merchant      |
|8540-4539-6212|711.99           |8540-4539-6212-2024-01-30|8              |2024-01-30T15:50:18.216827|2-day shipping   |Merchant      |
|1207-5305-6809|451.53           |1207-5305-6809-2024-01-30|27             |2024-01-30T15:50:19.431432|Overnight        |Merchant      |
|8841-6903-5597|274.35           |8841-6903-5597-2024-01-30|46             |2024-01-30T15:50:20.021068|Freight          |Merchant      |
|3002-3834-7450|923.4            |3002-3834-7450-2024-01-30|11             |2024-01-30T15:50:21.287097|Expedited        |Bexley        |
|6381-4358-8545|553.41           |6381-4358-8545-2024-01-30|3              |2024-01-30T15:50:22.803278|International    |Merchant      |
+--------------+-----------------+-------------------------+---------------+--------------------------+-----------------+--------------+
only showing top 20 rows

-------------------------------------------
Batch: 1
-------------------------------------------
+--------------+----------------+-------------------------+---------------+--------------------------+-----------------+--------------+
|order_number  |discounted_total|data_key                 |ship_to_city_id|order_date                |ship_method      |fufilment_type|
+--------------+----------------+-------------------------+---------------+--------------------------+-----------------+--------------+
|9089-5395-6646|757.35          |9089-5395-6646-2024-02-04|50             |2024-02-04T19:04:11.226381|Same-day delivery|Merchant      |
+--------------+----------------+-------------------------+---------------+--------------------------+-----------------+--------------+

-------------------------------------------
Batch: 2
-------------------------------------------
+--------------+----------------+-------------------------+---------------+--------------------------+--------------+--------------+
|order_number  |discounted_total|data_key                 |ship_to_city_id|order_date                |ship_method   |fufilment_type|
+--------------+----------------+-------------------------+---------------+--------------------------+--------------+--------------+
|3001-3344-9828|85.85           |3001-3344-9828-2024-02-04|32             |2024-02-04T19:04:11.952191|Freight       |Bexley        |
|1020-6289-6982|482.24          |1020-6289-6982-2024-02-04|41             |2024-02-04T19:04:13.367268|2-day shipping|Merchant      |
+--------------+----------------+-------------------------+---------------+--------------------------+--------------+--------------+

.....

-------------------------------------------
Batch: 165
-------------------------------------------
+--------------+----------------+-------------------------+---------------+--------------------------+-----------+--------------+
|order_number  |discounted_total|data_key                 |ship_to_city_id|order_date                |ship_method|fufilment_type|
+--------------+----------------+-------------------------+---------------+--------------------------+-----------+--------------+
|2053-4192-7379|860.2           |2053-4192-7379-2024-02-04|56             |2024-02-04T19:18:45.102280|Expedited  |Merchant      |
+--------------+----------------+-------------------------+---------------+--------------------------+-----------+--------------+



```

paste s3 offset window here

![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/e2090ad5-2ba1-4148-9cf0-4edb4a0c1b2e)


```
kubectl delete pod/bexley-spark-streaming-svc-driver -n spark-operator
pod "bexley-spark-streaming-svc-driver" deleted

recreated pod

kubectl get pods -A                                                   
NAMESPACE        NAME                                READY   STATUS    RESTARTS   AGE
kube-system      aws-node-gr5zb                      2/2     Running   0          3h25m
kube-system      aws-node-rwk9m                      2/2     Running   0          3h25m
kube-system      coredns-798c569cc7-q7h6c            1/1     Running   0          3h25m
kube-system      coredns-798c569cc7-wpqzt            1/1     Running   0          3h25m
kube-system      kube-proxy-gq2j7                    1/1     Running   0          3h25m
kube-system      kube-proxy-hl557                    1/1     Running   0          3h25m
logging          fluent-bit-8j9xb                    1/1     Running   0          176m
logging          fluent-bit-8wrlk                    1/1     Running   0          176m
spark-operator   bexley-spark-streaming-svc-driver   1/1     Running   0          36s
spark-operator   spark-operator-675d97df85-4sqd5     1/1     Running   0          158m

lets view if it starts from last offset

kubectl logs  -f pod/bexley-spark-streaming-svc-driver -n spark-operator

Select specific colums from the data frame, transforming alongside
printing out the schema for the transformed kafka feed
root
 |-- order_number: string (nullable = true)
 |-- discounted_total: double (nullable = true)
 |-- data_key: string (nullable = false)
 |-- ship_to_city_id: integer (nullable = true)
 |-- order_date: string (nullable = true)
 |-- ship_method: string (nullable = true)
 |-- fufilment_type: string (nullable = false)

Initial Transformation of Raw Kafka Stream Successful ...
{"@timestamp":"2024-02-04T19:15:40.152Z","log.level":"info","message":"JSON Dataframe Transformed","ecs":{"version":"1.6.0"},"http":{"request":{"body":{"content":"JSON Dataframe Transformed"}}},"log":{"logger":"__main__","origin":{"file":{"line":411,"name":"bexley_spark_stream_msk_es_05.py"},"function":"transform_json_message"},"original":"JSON Dataframe Transformed"},"process":{"name":"MainProcess","pid":80,"thread":{"id":140382534520640,"name":"MainThread"}}}
writing enriched data set to console ...
-------------------------------------------
Batch: 166
-------------------------------------------
+--------------+----------------+-------------------------+---------------+--------------------------+-----------+--------------+
|order_number  |discounted_total|data_key                 |ship_to_city_id|order_date                |ship_method|fufilment_type|
+--------------+----------------+-------------------------+---------------+--------------------------+-----------+--------------+
|8437-3139-7250|817.29          |8437-3139-7250-2024-02-04|19             |2024-02-04T19:18:46.104910|Freight    |Bexley        |
+--------------+----------------+-------------------------+---------------+--------------------------+-----------+--------------+

-------------------------------------------
Batch: 167
-------------------------------------------
+--------------+----------------+-------------------------+---------------+--------------------------+-------------+--------------+
|order_number  |discounted_total|data_key                 |ship_to_city_id|order_date                |ship_method  |fufilment_type|
+--------------+----------------+-------------------------+---------------+--------------------------+-------------+--------------+
|3706-3296-9177|584.32          |3706-3296-9177-2024-02-04|22             |2024-02-04T19:18:46.885017|Freight      |Bexley        |
|7001-3828-8571|872.64          |7001-3828-8571-2024-02-04|4              |2024-02-04T19:18:47.899856|International|Bexley        |
|2028-6576-8083|1128.11         |2028-6576-8083-2024-02-04|4              |2024-02-04T19:18:48.703440|Expedited    |Merchant      |
|7546-3260-7507|395.85          |7546-3260-7507-2024-02-04|49             |2024-02-04T19:18:50.155353|International|Bexley        |
+--------------+----------------+-------------------------+---------------+--------------------------+-------------+--------------+

-------------------------------------------
Batch: 168
-------------------------------------------
+--------------+----------------+-------------------------+---------------+--------------------------+-----------+--------------+
|order_number  |discounted_total|data_key                 |ship_to_city_id|order_date                |ship_method|fufilment_type|
+--------------+----------------+-------------------------+---------------+--------------------------+-----------+--------------+
|3520-5556-6592|31.35           |3520-5556-6592-2024-02-04|14             |2024-02-04T19:18:51.685728|Overnight  |Merchant      |
+--------------+----------------+-------------------------+---------------+--------------------------+-----------+--------------+

```
quick query

![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/7cdff835-0bd4-4f6c-91c0-62e3261bb404)



![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/eaebf1d6-679d-4745-888c-ec8bb4ceb07a)

![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/41a7811b-f8f4-45be-910e-ef0fb7d3e16d)


delete infra

![image](https://github.com/addyclement/spark-streaming-kafka-k8s-terraform-gitlab/assets/9949038/4c638600-b067-4b5d-a9d6-8f1a279a3963)

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
