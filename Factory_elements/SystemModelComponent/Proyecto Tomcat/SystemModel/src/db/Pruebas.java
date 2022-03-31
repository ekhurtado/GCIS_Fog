package db;

public class Pruebas {
	
	public static void main(String[] args) {
        System.out.println("Connecting with SQLite DB...");

        System.out.println("Getting applications table:");
        String result = DBDataManager.getInstance().getApplications();
        System.out.println(result);
    }

}
