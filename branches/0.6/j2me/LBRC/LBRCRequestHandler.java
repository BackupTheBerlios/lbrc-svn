package LBRC;
import org.json.me.*;

public interface LBRCRequestHandler {
	public void handleRequest(JSONObject obj) throws JSONException;
}