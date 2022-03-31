package db;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.sql.*;
import java.util.Properties;
import java.util.logging.Level;
import java.util.logging.Logger;

public class DBManager {

//    String sqlite_path = "C:\\Users\\839073\\Documents\\Proyecto viejo SystemModel\\smc.db";
	String sqlite_path = "/system_model/data/smc.db";
    Connection conn = null;


    private void conOpen() {
        try {


            //String url = "jdbc:sqlite::resource:dasiapp.db";
//			String sqlite_path = "/home/ekaitzhara/Documentos/UNI/InformazioSistemenAnalisia/3_partziala/datubasea.db";
//            String sqlite_path = properties.getProperty("sqlite_path");;
//            sqlite_path = sqlite_path.replace('/', File.separatorChar);

            sqlite_path = sqlite_path.replace('\\', File.separatorChar);
            String url = "jdbc:sqlite:" + sqlite_path;
            //url=url.replace("resources/main/main/", "data/dasiapp.db");
            System.out.println(url);

            Class.forName("org.sqlite.JDBC").getConstructor().newInstance();

            conn = (Connection) DriverManager.getConnection(url);
            conn.setAutoCommit(false);
            System.out.println("Database connection established");
        } catch (Exception e) {
            System.err.println("Cannot connect to database server " + e);
        }
    }

    private void conClose() {

        if (conn != null)
            try {
                conn.close();
            } catch (SQLException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }

        System.out.println("Database connection terminated");

    }

    private ResultSet query(Statement s, String query) {

        ResultSet rs = null;

        try {
            rs = s.executeQuery(query);
            conn.commit();
        } catch (SQLException e) {
            e.printStackTrace();
        }

        return rs;
    }

    // Singleton pattern
    private static DBManager instance = new DBManager();

    private DBManager() {
        this.conOpen();

    }

    public static DBManager getInstance() {
        return instance;
    }

    public ResultSet execSQL(String query) {
        int count = 0;
        Statement s = null;
        ResultSet rs = null;

        try {
            s = (Statement) conn.createStatement();
            if (query.toLowerCase().indexOf("select") == 0) {
                // select agindu bat
                rs = this.query(s, query);

            } else {
                // update, delete, create agindu bat
                count = s.executeUpdate(query);
                conn.commit();
                System.out.println(count + " rows affected");
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }

        return rs;
    }

}
