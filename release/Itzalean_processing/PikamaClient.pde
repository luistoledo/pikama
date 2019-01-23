import websockets.*;
import java.awt.geom.Line2D;


public static class PikamaClient {

  // contiene una lista de los últimos objetos encontrados por la cámara
  static JSONArray blobs;

  // el objeto websocket que se conecta al server
  static WebsocketClient wsc;

  // referencia al applet // puede que esté de más, solo se usa al conectar
  static PApplet applet;

  // referencia a la url de conexión
  static String url;
  
  // indica si comenzamos a recibir datos
  public static boolean started = false;

  // la referencia del tamaño máximo del espacio de detección
  public static int width, height;

  public static float scalex, scaley;


  PikamaClient() {
  }


  public static void connect() {
    if (applet != null && url != null) {
      connect(applet, url);
    }
  }

  // Instrucción de conexión
  public static void connect(PApplet t, String server) {
    started = false;
    applet = t;
    url = server;

    println("/// trying connection");
    if (wsc != null)  wsc.dispose();  
    wsc= new WebsocketClient(applet, "ws://" + url + "/blobs");

    // String[] frameSize = loadString("https://"+url);
    // width = 500;
    // height = 281;
  }

  // Instrucción de descconexión
  public static void disconnect() {
    started = false;

    println("/// disconnecting");
    if (wsc != null)  wsc.dispose();
  }



  static void normalizeBlobs(){
    JSONArray r = PikamaClient.blobs;
    
    for (int i=0; i<PikamaClient.blobs.size(); i++) {
      int[] p = PikamaClient.blobs.getJSONArray(i).getIntArray();
      p[0] *= scalex;
      p[1] *= scaley;
      p[2] *= (scalex+scaley)/2;
      String sa = "["+p[0]+","+p[1]+","+p[2]+"]";
      r.setJSONArray(i, JSONArray.parse(sa));
      // JSONArray ja = JSONArray.parse(sa);
    }
    
    PikamaClient.blobs = r;
  }






  public static void draw() {
    applet.pushMatrix();
    applet.stroke(200, 0, 0, 50);
    applet.fill(0, 200, 0, 20);

    if (blobs!=null) {
      for (int i=0; i<blobs.size(); i++) {
        int[] p = blobs.getJSONArray(i).getIntArray();
        int x = p[0];
        int y = p[1];
        int r = p[2];
        applet.ellipse(x, y, r, r);
      }
    }
    applet.popMatrix();
  }





  public static void CommandServer(String cmd) {
    applet.loadStrings("http://" + url + "/do/"+cmd);
  }

  public static void ResetBGSubtraction() {
    applet.loadStrings("http://" + url + "/do/reset");
  }


  // Calcula la cercanía de todos los blobs, contra todos los
  // segmentos de la linea
  // responde 1 sola coincidencia
  // 0: ningúna cercanía
  // 1: el blob más cercano, pasa cerca de la linea
  // 2: el blob más cercano, cruza la linea
  //    revisa todos contra todos buscando resultado 1, si no, regresa 0, si si, busca un 2 en el que resulte 1
  public static int ProximityToLines(Linea linea) {
    if (!started) return 0;
    if (blobs.size()==0) return 0;

    // normalizeBlobs();

    int bestProximity = 0;

    for (int i=0; i<blobs.size(); i++) {
      int[] p = blobs.getJSONArray(i).getIntArray();
      
      for (int j=1; j<linea.max_segmentos; j++) {
        double d = Line2D.ptSegDistSq(
          linea.puntos[j-1].x, linea.puntos[j-1].y, 
          linea.puntos[j].x, linea.puntos[j].y,
          p[0], p[1]);
        if (d < p[2]) {
          return 2;
        }
        if ( d<(p[2]*p[2]) ) {
          return 1;
        }
      }
    }
    return bestProximity;
  }
}


// Recibe los blobs del server de pikAMA
void webSocketEvent(String msg) {

  if (msg.startsWith("[")) {
    PikamaClient.started = true;

    JSONArray payload = parseJSONArray (msg);

    PikamaClient.width = payload.getJSONArray(payload.size()-1).getIntArray()[0];
    PikamaClient.height = payload.getJSONArray(payload.size()-1).getIntArray()[1];
    payload.remove(payload.size()-1);

    if (payload != null) {
      PikamaClient.blobs = payload;
    }

    PikamaClient.normalizeBlobs();
  }
}
