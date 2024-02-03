import json
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from kafka.errors import KafkaError
from faker import Faker
from random import randint,choice
import datetime,time
from json import JSONEncoder
from bexley_load_auth_from_secrets_manager_v01 import get_secret_from_sm
from decouple import config
import socket
from datetime import datetime


freight_min, freight_max = 1,20
ship_to_city_id_min , ship_to_city_id_max = 1,66
discount_applied_min, discount_applied_max = 1,20
order_total_min, order_total_max = 30, 1200
order_id_min, order_id_max = 1000,9000
order_date_min, order_date_max = '-372d','-373d'
shipping_methods = ['Expedited','Overnight','2-day shipping','Flat rate','Same-day delivery','International','Freight']
customer_id_min, customer_id_max = 100, 90000

# random basket params
order_qty_min, order_qty_max = 1,9
product_id_min, product_id_max = 1, 20000


def main():
     
    # retrive kafka details from secrets manager

    #*****# Load Secret ids from environment variable #*****#

    kafka_secret_id = config('bexley_kafka_secret_id')
    
    #*****# Decrypt auth secrets stored in Secrets Manager *******#

    kafka_secrets = get_secret_from_sm(kafka_secret_id)
    
    #***************# Load details for kafka ***************#

    kafka_topic_name = kafka_secrets['bexkley_topic']
    kafka_bootstrap_servers = kafka_secrets['bootstrap_servers']
    kafka_sasl_plain_username = kafka_secrets['sasl_plain_username']
    kafka_sasl_plain_password = kafka_secrets['sasl_plain_password']
    kafka_sasl_mechanism = kafka_secrets['sasl_mechanism']
    kafka_security_protocol = kafka_secrets['security_protocol']

    #print("user :" , kafka_sasl_plain_username)
    #print("password : ", kafka_sasl_plain_password)
    # parameters for order basket

    loops = 200

    i=0

    while i < loops:

        fake = Faker("en_GB")
        
        min_basket_items = 1
        max_basket_items = 20
        
        kafka_message_key = "blackfiday_sales"

        print("generate order message...")

        kafka_message_value = generate_order_basket(basket_min=min_basket_items,basket_max=max_basket_items)

        print("post order message to kafka queue")

        
        post_message_to_kafka(kafka_bootstrap_server=kafka_bootstrap_servers,
                              sasl_user=kafka_sasl_plain_username,
                              sasl_password=kafka_sasl_plain_password, 
                              security_protocol=kafka_security_protocol,
                              sasl_mechanism=kafka_sasl_mechanism,
                              kafka_topic=kafka_topic_name,
                              message_key = kafka_message_key,
                              message_value =kafka_message_value)
        

        time.sleep(1)
        i=i+1
    
    # list_kafka_topics(kafka_bootstrap_server=kafka_bootstrap_servers,sasl_user=kafka_sasl_plain_username,sasl_password=kafka_sasl_plain_password)

# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
           

#define a custom order with variable number of items

# order_date = gen_datetime(min_year=2022)

def generate_order_basket(basket_min, basket_max):

    fake = Faker('en_GB')

    order_no = "{p1}-{p2}-{p3}".format(p1=randint(1000,9999),p2=randint(3000,6999), p3=randint(5000,9999))
    order_timestamp = datetime.now()

    # initialise an empty basket, this could hold up a variable number of distinct items

    basket = []

    for item in range(randint(basket_min,basket_max)):
        basket.append({
                "order_qty": randint(order_qty_min,order_qty_max),
                "product_id": randint(product_id_min,product_id_max),
                "is_discounted": bool(choice([True, False]))
        })
    # order details
    # use sales order kwargs here

    sales_order ={
            "freight": fake.random_int(freight_min, freight_max),
            "order_id": randint(order_id_min,order_id_max),
            "customer_id": fake.random_int(min=customer_id_min, max=customer_id_max), 
            "ship_method": choice(shipping_methods),
            "order_date": order_timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            "order_total": randint(order_total_min,order_total_max),
            "order_basket": basket, # to be dynamically populated from the basket for loop above
            "order_number" : order_no,
            "ship_to_city_id":fake.random_int(ship_to_city_id_min, ship_to_city_id_max),
            "discount_applied":fake.random_int(discount_applied_min, discount_applied_max)
        }
    
    print(DateTimeEncoder().encode(sales_order))
    return (DateTimeEncoder().encode(sales_order))

# function to post message to kafka topic

def post_message_to_kafka(kafka_topic,message_key,message_value,kafka_bootstrap_server, sasl_user, sasl_password,sasl_mechanism,security_protocol):

    # define config for kafka  
    """
    producer = Producer(
    'bootstrap.server':[kafka_bootstrap_server],
    'sasl.mechanism':'SCRAM-SHA-256',
    'security.protocol':'SASL_SSL',
    'sasl.username':sasl_user,
    'sasl.password':sasl_password,
    value_serializer=lambda v: (v).encode('ascii'),
    key_serializer=lambda v: (v).encode('ascii')
    )
    """
   
    b_server = kafka_bootstrap_server
    # print("kafka server address : ")
    # print(kafka_bootstrap_server)

    config = {'bootstrap.servers':kafka_bootstrap_server,
            'sasl.mechanism':sasl_mechanism,
            'security.protocol':security_protocol,
            'sasl.username':sasl_user,
            'sasl.password':sasl_password,
            'enable.idempotence': True,
            'acks': 'all',
            'retries': 1,
            'client.id': socket.gethostname()}
    # enable try catch
    # https://dev.to/sats268842/best-practices-for-kafka-in-python-2me5
    # https://www.programcreek.com/python/example/92970/kafka.errors.KafkaError
    # https://copyprogramming.com/howto/confluent-python-kafka-producer-send-callback-message-offset-returns-0

    config_2= {
            'bootstrap.servers':  '**********',
            'security.protocol':  '**********',
            'ssl.ca.location': '**********',
            'client.id': socket.gethostname(),
            'enable.idempotence': True,
            'acks': 'all',
            'retries': 10,
            'compression.type': 'gzip',
            'max.in.flight.requests.per.connection': 5,
            'compression.codec': 'gzip'
            }
    
    try :

        kafka_producer = Producer(config)

        kafka_producer.produce(topic=kafka_topic,
                            key=message_key,
                            value=message_value)
        kafka_producer.flush()

    except KafkaError as error :
        print("An error occured : ", error)


def list_kafka_topics(kafka_bootstrap_server, sasl_user, sasl_password):

    # define config for kafka  
    """
    producer = Producer(
    'bootstrap.server':[kafka_bootstrap_server],
    'sasl.mechanism':'SCRAM-SHA-256',
    'security.protocol':'SASL_SSL',
    'sasl.username':sasl_user,
    'sasl.password':sasl_password,
    value_serializer=lambda v: (v).encode('ascii'),
    key_serializer=lambda v: (v).encode('ascii')
    )
    """
   
    b_server = kafka_bootstrap_server
    print("kafka server address : ")
    print(kafka_bootstrap_server)

    config = {'bootstrap.servers':kafka_bootstrap_server,
            'sasl.mechanism':'SCRAM-SHA-512',
            'security.protocol':'SASL_SSL',
            'sasl.username':sasl_user,
            'sasl.password':sasl_password,
            'client.id': socket.gethostname()}
    # enable try catch
    # https://dev.to/sats268842/best-practices-for-kafka-in-python-2me5
    # https://www.programcreek.com/python/example/92970/kafka.errors.KafkaError
    # https://copyprogramming.com/howto/confluent-python-kafka-producer-send-callback-message-offset-returns-0

    config_2= {
            'bootstrap.servers':  '**********',
            'security.protocol':  '**********',
            'ssl.ca.location': '**********',
            'client.id': socket.gethostname(),
            'enable.idempotence': True,
            'acks': 'all',
            'retries': 10,
            'compression.type': 'gzip',
            'max.in.flight.requests.per.connection': 5,
            'compression.codec': 'gzip'
            }
    
    try :

        admin_client = AdminClient(config)

        """
        new_list = []
        new_list.append(NewTopic("bxl-stream-02",2,2))
        admin_client.create_topics(new_list)
        print("topic created")
        """
        
        topic_list = admin_client.list_topics().topics
        print("Topics in the Kafka cluster:")
        for topic in topic_list:
            print(topic)
        

    except KafkaError as error :
        print("An error occured : ", error)

if __name__ == "__main__":
    main()
