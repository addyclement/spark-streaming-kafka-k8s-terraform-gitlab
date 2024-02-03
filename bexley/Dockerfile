#spark 3.5 is already available 
FROM bitnami/spark:3.4.1 

#update os and install curl
USER root
RUN apt update -y
RUN apt upgrade -y
RUN apt install curl -y

# download mysql connector and elastic-spark jars for connectivity to datastores
RUN curl https://repo1.maven.org/maven2/mysql/mysql-connector-java/5.1.49/mysql-connector-java-5.1.49.jar --output /opt/bitnami/spark/jars/mysql-connector-java-5.1.49.jar
RUN curl https://repo.maven.apache.org/maven2/org/elasticsearch/elasticsearch-spark-30_2.12/8.2.1/elasticsearch-spark-30_2.12-8.2.1.jar --output /opt/bitnami/spark/jars/elasticsearch-spark-30_2.12-8.2.1.jar

# upload and install dependencies/packages
COPY ./requirements.txt /
RUN pip install -r /requirements.txt

EXPOSE 4040 8888 8080 8081


# set workdirectory to the source code path
# mapping this container path to my local path during dev
# downloading code from git repo to this path, via the compose file
WORKDIR /opt/bitnami/spark/code

# add code folder from gitlab project to container image
COPY code /opt/bitnami/spark/code
