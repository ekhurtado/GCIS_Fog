package pruebasKafka;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.TimeZone;

public class PruebaHora {
	
	public static void main(String[] args) throws ParseException {
		String hora = "2023/2/9";
		System.out.println(hora);
		
		Date date = new Date();
		
		DateFormat dateFormat = new SimpleDateFormat("YYYY/MM/dd");
		dateFormat.setTimeZone(TimeZone.getTimeZone("Europe/Madrid"));
		String fecha = dateFormat.format(date);
		
		
		fecha = "2023/01/01";
		System.out.println(fecha);
		if (fecha.contains("/0")) {
			fecha = fecha.replace("/0", "/");
			System.out.println(fecha);
		}
		
		Date date2 = dateFormat.parse(hora);
		String fecha2 = dateFormat.format(date2);
		System.out.println(fecha2);
		
		if (hora.equals(fecha))
			System.out.println("IGUALES");
		else
			System.out.println("DIFERENTES");

	}

}
