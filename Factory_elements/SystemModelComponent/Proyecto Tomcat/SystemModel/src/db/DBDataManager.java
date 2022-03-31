package db;

import java.sql.ResultSet;
import java.sql.SQLException;

public class DBDataManager {

    // Singleton pattern
    private static DBDataManager instance = new DBDataManager();

    private DBDataManager() {

    }

    public static DBDataManager getInstance() {
        return instance;
    }

    public String getApplications() {

        DBManager dbKud = DBManager.getInstance();
        ResultSet rs=null;
        String query = "SELECT * FROM applications";
        rs = dbKud.execSQL(query);

        StringBuilder sb = new StringBuilder();

        try {
            while (rs.next()) {

                String id = rs.getString("id");
                String name = rs.getString("name");

                sb.append(id + " - " + name + "\n");

            }
        } catch (SQLException e) {
            e.printStackTrace();
        }

        return sb.toString();
    }
    
    

}
