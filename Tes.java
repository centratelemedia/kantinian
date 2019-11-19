import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class Tes {
    public static void main(String[] args){
        try {
            String URL_JSON = "http://kantinian.id/dev/index.php";
            URL url = new URL(URL_JSON);
            URLConnection request = url.openConnection();
            request.connect();

            JsonParser jsonParser = new JsonParser();
            JsonElement jsonElement = jsonParser.parse(new InputStreamReader((InputStream) request.getContent()));
            JsonObject jsonObject = jsonElement.getAsJsonObject();
            JsonArray jsonArray = jsonObject.getAsJsonArray("result");

            for (Object o: jsonArray) {
                if(o instanceof JsonObject){
                    String id = ((JsonObject) o).get("id").toString();
                    String nama = ((JsonObject) o).get("nama").toString();
                    String template = ((JsonObject) o).get("template").toString();
                    System.out.println(id + nama + template);
                }
            }
        } catch (Exception ex) {
            System.out.println("Error getPayload: " + ex.toString());
        }
    }
}