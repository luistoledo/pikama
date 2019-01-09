import oscP5.*;
import netP5.*;

OscP5 oscP5;

void setup() {
  size(400,400);
  frameRate(25);
  
  connectToOSC();
}

void connectToOSC() {
  OscProperties properties = new OscProperties();
  properties.setRemoteAddress("127.0.0.1",5005);
  properties.setListeningPort(12000);
  properties.setSRSP(OscProperties.ON);
  properties.setDatagramSize(1024);
  
  oscP5 = new OscP5(this,properties);
  
  println(properties.toString());
}


void subscribeOSC() {
  OscMessage myMessage = new  OscMessage("/subscribe");
  myMessage.add(200);
  oscP5.send(myMessage);
}

void mousePressed() {
  subscribeOSC();
}


void draw() {
  fill(0,10);
  rect(0,0,width,height);
}

void oscEvent(OscMessage msg) {
  if (msg.checkTypetag("iiii")) {
    ContourRect c = new ContourRect(
        msg.get(1).intValue(), 
        msg.get(0).intValue(),
        msg.get(2).intValue(),
        msg.get(3).intValue()
    );
    println("T:"+millis() + ">> " + c);
    fill(200,10,0);
    rect(c.x,c.y,c.w,c.h);
  }
  print("### received an osc message.");
  print(" addrpattern: "+msg.addrPattern());
  println(" typetag: "+msg.typetag());
}

class ContourRect {
  int x,y,w,h;
  ContourRect(int x, int y, int w, int h) {
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;
  }
  String toString() {
    return "x:" + this.x +
    " y:" + this.y +
    " w:" + this.w +
    " h:" + this.h;
  }
}
