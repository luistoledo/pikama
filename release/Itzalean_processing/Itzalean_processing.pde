int MAX_SEGMENTOS = 10;
boolean DEBUG=false;
int MAX_TIEMPONEGRO = 5000;

String PIKAMA_SERVER_URL = "127.0.0.1:12345";

// la linea actual que se dibuja
Linea linea;

// obtiene los usuarios moviéndose
// PikamaClient usuarios;
// MotionDetector usuarios; // webcam opencv

// estado general NEGRO o LINEA
int estado = 0;

// estados de las propiedades de la linea
boolean dibujarSilueta = true;
boolean animar_linea=false;
boolean repetir_linea=false;

// timer para cuándo ocultar la linea
int alarmaDeLinea = 0;

float camScreenScaleX=1, camScreenScaleY=1;
boolean escalaEstablecida = false;

final int ESTADO_NEGRO = 0;
final int ESTADO_LINEA = 1;



void setup() {
  size(640, 360);
  // fullScreen();
  frameRate(24);

  linea = new Linea(MAX_SEGMENTOS); //
  PikamaClient.connect(this, PIKAMA_SERVER_URL);

  EstadoALinea();
}


void draw() {
  // actualiza la escala entre la pantalla y la cámara
  // así la posición de los blobs y las lineas coincidirán
  if (!escalaEstablecida) {
    if (PikamaClient.started) {
      camScreenScaleX = float(width)/float(PikamaClient.width);
      camScreenScaleY = float(height)/float(PikamaClient.height);
      escalaEstablecida = true;
      PikamaClient.scalex=camScreenScaleX; PikamaClient.scaley=camScreenScaleY;
    }
  }


  if (DEBUG) {
      PikamaClient.draw();
  }

  if (estado == ESTADO_NEGRO) {
    noStroke();
    fill(0, 50);
    rect(0, 0, width, height);

    int p = PikamaClient.ProximityToLines(linea);
    
    if (p == 2) {
      println("=== objeto intersecta la linea");
      EstadoALinea();
      // sonido alto
    }
    if (p == 1) {
      println("=== objeto se acerca a linea");
      EstadoALinea();
      // sonido medio
    }

    if (DEBUG) {
      linea.dibuja();
    }
  }

  if (estado == ESTADO_LINEA) {
    noStroke();
    fill(0, 20);
    rect(0, 0, width, height);
    anima_linea();
    repite_linea();
    linea.dibuja();

    if (alarmaDeLinea - millis() < 0) {
      println("<<< termina tiempo de mostrar linea");
      EstadoANegro();
    }
  }
}



void EstadoANegro() {
  estado = ESTADO_NEGRO;
  println("ESTADO NEGRO");
  PikamaClient.ResetBGSubtraction();
}
void EstadoALinea() {
  animar_linea=true;
  alarmaDeLinea = millis() + MAX_TIEMPONEGRO;
  recargaLinea();
  estado = ESTADO_LINEA;
  println("ESTADO LINEA");
}


void recargaLinea() {
  linea.nuevaAleatoriaVertical(1);
}




void keyPressed() {
  // linea aleatoria de arriba a abajo
  if (keyCode=='1') {
    //linea.nuevaAleatoriaVertical(1);
    //animar_linea=true;
    //repetir_linea=false;
    EstadoALinea();
  }
  // linea vertical a la mitad de la ventana
  else if (keyCode=='2') {
    linea.nuevaFija(width/2, 0, width/2, height, 1);
    EstadoALinea();
  }
  // linea vertical desde arriba mitad, hasta el ratón
  else if (keyCode=='3') {
    linea.nuevaFija(width/2, 0, mouseX, mouseY, 1);
    EstadoALinea();
  }
  else if (keyCode=='4') {
    linea.nuevaLineaEncierrona();
    EstadoALinea();
  }
  //iosune
  else if (keyCode=='6') {
    repetir_linea=true; 
    EstadoALinea();
  }

  else if (keyCode=='S') {
    dibujarSilueta = !dibujarSilueta;
    println("silueta: "+dibujarSilueta);
  }
  else if (keyCode=='D') {
    DEBUG = !DEBUG;
    println("DEBUG: "+DEBUG);
  }
  else if (keyCode=='R') {
    PikamaClient.ResetBGSubtraction();
  }
  else if (keyCode=='C') {
    PikamaClient.connect();
    println("RECONNECT SERVER: "+DEBUG);
    escalaEstablecida=false;
  }

  if (keyCode=='T') {
    PikamaClient.CommandServer("threshold");
  }
  else if (keyCode=='M') {
    PikamaClient.CommandServer("mirror_horizontal");
  }
  else if (keyCode=='N') {
    PikamaClient.CommandServer("mirror_vertical");
  }
  else if (keyCode=='P') {
    PikamaClient.CommandServer("max_area");
  }
  else if (keyCode=='O') {
    PikamaClient.CommandServer("max_area");
  }
  else if (keyCode=='L') {
    PikamaClient.CommandServer("threshold");
  }
  else if (keyCode=='K') {
    // PikamaClient.CommandServer("max_area");
  }
  else if (keyCode=='J') {
    // PikamaClient.CommandServer("max_area");
  }

  // altera cada punto de una linea ya creada
  else if (keyCode=='9') {
    linea.muta(3);
    EstadoALinea();
  }
  // dibuja negro
  else if (keyCode=='0') {
    EstadoANegro();
  }
}


//iosune
void anima_linea() {
  if (animar_linea==true) {
    if (frameCount % 1 < 0.1) {
      linea.muta(3, 0); 
      //estado = ESTADO_LINEA;
    }
  }
}
//iosune
void repite_linea() {
  if (repetir_linea==true) {
    animar_linea=false;
    for (int x=0; x<width; x=x+20) {
      linea.muta(x, 0);// cambiarl la x de esta
    }
    for (int x=0; x<0; x=x-20) {
      linea.muta(x, 0);
    }
  }
}
