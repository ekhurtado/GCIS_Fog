package pruebasKafka;

import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.Random;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.json.simple.JSONObject;

import org.springframework.kafka.core.DefaultKafkaProducerFactory;
//import org.springframework.kafka.support.serializer.JsonSerializer;
import org.apache.kafka.connect.json.JsonSerializer;


import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import org.apache.kafka.common.serialization.StringSerializer;


public class PruebaProducer {
	
	public static String IP_server = "mi-cluster-mensajeria-kafka-bootstrap.kafka-ns";
	
	public static void main(String[] args) {
		
		System.out.println("Comienza prueba producer");
		
//		Map<String, Object> props = new HashMap<>();
//        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, IP_server + ":9092");

//        DefaultKafkaProducerFactory<String, JsonNode> kafkaProducerFactory = new DefaultKafkaProducerFactory<>(props, new StringSerializer(), new JsonSerializer<>());
//        DefaultKafkaProducerFactory<String, JsonNode> kafkaProducerFactory = new DefaultKafkaProducerFactory<>(props, new StringSerializer(), new JsonSerializer());
//        producerFactory.createProducer()

        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, IP_server + ":9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
//        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.ACKS_CONFIG, "1");
		
//		Producer<String, String> producer = kafkaProducerFactory.createProducer();
//		Producer<String, JsonNode> producer = kafkaProducerFactory.createProducer();
        
        KafkaProducer<String, String> producer = new KafkaProducer<>(props);
//        KafkaProducer<String, JsonNode> producer = new KafkaProducer<>(props);

		while (true) {
		
			Random r = new Random();
			int limiteRandom = 100;
			
//			JSONObject jsonData = new JSONObject();
//			jsonData.put("numero", r.nextInt(limiteRandom));
//			System.out.println(jsonData.toJSONString());
			String key = "prueba-producer";
			
			
			String newString = "{\"numero\": " + r.nextInt(limiteRandom) + "}";
			ObjectMapper mapper = new ObjectMapper();
			JsonNode jsonNode = null;
			try {
				jsonNode = mapper.readTree(newString);
			} catch (JsonProcessingException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
			
			System.out.println(jsonNode.toString());
			
			
			//prepare the record
//			String recordValue = jsonData.toJSONString();
//			ProducerRecord<String, JsonNode> record = new ProducerRecord<String, JsonNode>("topicos-datos-crudos", key, jsonNode);
			ProducerRecord<String, String> record = new ProducerRecord<>("topico-datos-crudos", key, jsonNode.toString());
			
			//Sending message to Kafka Broker
			producer.send(record);
			producer.flush();
			
			try {
				Thread.sleep(5000); // Esperamos 2 segundos
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		
//		producer.close();
		
	}

}
