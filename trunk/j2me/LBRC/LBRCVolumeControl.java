package LBRC;

import javax.microedition.lcdui.*;
import org.json.*;
import java.util.*;

public class LBRCVolumeControl extends LBRCShowModuleFormular {
	private Hashtable volume_data;
	private Hashtable visible_elements;
	
	LBRCVolumeControl(LBRCSenderController parent, String name) {
		super(parent, name);
		visible_elements = new Hashtable();
		volume_data = new Hashtable();
	}
	
	public synchronized void handleRequest(JSONObject obj) {
		if (! obj.getString("type").equals(this.name)) return;
		String command = obj.getString("command");
		if(command.equals("updateVolumes")) {
			JSONArray volumes = obj.getJSONArray("volumeData");
			synchronized(this.volume_data) {
				this.volume_data.clear();
				for(int i=0;i<volumes.length();i++) {
					JSONArray contents = volumes.getJSONArray(i);
					this.volume_data.put(contents.getString(0), contents);
				}
				updateVolume();
			}
		}

	}
	
	private void updateVolume() {
		Enumeration enum_key_visible_elements = visible_elements.keys();
		while(enum_key_visible_elements.hasMoreElements()){
			String key = (String) enum_key_visible_elements.nextElement();
			if ( ! volume_data.containsKey(key) ) {
				Integer element = (Integer) visible_elements.get(key);
				this.delete(element.intValue());
				visible_elements.remove(key);
			}
		}
		Enumeration enum_key_volume_data = volume_data.keys();
		while(enum_key_volume_data.hasMoreElements()) {
			String key = (String) enum_key_volume_data.nextElement();
			JSONArray vol_dat = (JSONArray) volume_data.get(key);
			if ( ! visible_elements.contains(key)) {
				Gauge gauge = new Gauge(vol_dat.getString(0), false, 100, vol_dat.getInt(1)); 
				visible_elements.put(key, gauge);
			} else {
				Gauge gauge = (Gauge) visible_elements.get(key);
				gauge.setValue(vol_dat.getInt(1));
			}
		}
	}
}
