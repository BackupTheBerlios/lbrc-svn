package LBRC;

import javax.bluetooth.LocalDevice;
import javax.microedition.io.Connector;
import javax.microedition.io.StreamConnection;
import java.io.IOException;
import java.io.OutputStream;
import javax.bluetooth.*;
import java.lang.Integer;

final class LBRCBT implements Runnable {
	private LocalDevice localDevice;
    private Thread senderThread;
	private L2CAPConnection conn;
    private OutputStream out;
    private LBRC parent;
    private String URL;

	LBRCBT(LBRC parent, String URL ) {
		senderThread = new Thread(this);
        this.parent = parent;
        this.URL = URL;
		senderThread.start();
	}

	public void sendKey(int keyCode, byte mapping) {
		if(conn != null){
		    byte[] data = new byte[5];
            // Encode int keyCode to binary array
            // mapping allows distinguishing press from release
            data[0] = mapping;
            for (int i = 0; i < 4; i++) {
                int offset = (3 - i) * 8;
                data[i+1] = (byte) ((keyCode >>> offset) & 0xFF);
            }
			try {
			    conn.send(data);
			} catch (Exception e) {
			    parent.do_alert("Can't send data: " + e, 4000);
                parent.close_remote_service();
			}
		}
	}

	public void run() {
		try {
			conn = (L2CAPConnection)Connector.open(this.URL);
		} catch (Exception e) {
            parent.do_alert("Bluetooth Connection Failed", 4000);
            parent.close_remote_service();
		}
	}
	
	public void shutdown() {
		try {
			conn.close();
		} catch (IOException e) {}
		try {
			senderThread.join();
		} catch (InterruptedException e) {}
	}
}
