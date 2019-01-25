int MAX_SEGMENTOS = 10;
boolean DEBUG=false;
int MAX_TIEMPOLINEA = 5000;
int MAX_TIEMPOARBOL = 2000;
int MAX_TIEMPONEGRO = 2000;

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

boolean show_help = false;

int soundTimeout = 500000; // = 20 min => 500000/1000/24
int soundTimer = millis();

// timer para cuándo ocultar la linea
int alarmaDeLinea = 0;
int alarmaDeArbol = 0;
int alarmaDeNegro = 0;

float camScreenScaleX=1, camScreenScaleY=1;
boolean escalaEstablecida = false;

float factorSonidoLejano = 2, factorSonidoCercano = 10;

final int ESTADO_NEGRO = 0;
final int ESTADO_LINEA = 1;
final int ESTADO_ARBOL = 2;
final int ESTADO_BUSCANDO = 3;
// linea > negro > buscando > arbol > linea

int resetBGTimer = -1;


Trees trees;


void setup() {
  // size(640, 360);
  fullScreen();
  frameRate(24);
  noCursor();

  linea = new Linea(MAX_SEGMENTOS); //
  trees = new Trees();

  PikamaClient.connect(this, PIKAMA_SERVER_URL);

  loadSounds();
  
  EstadoALinea();
}


void draw() {

  // if (resetBGTimer != -1) {
  //   resetBGTimer --;
  //   if (resetBGTimer <= 0) {
  //     PikamaClient.ResetBGSubtraction();
  //     resetBGTimer = -1;
  //     println(millis() + " : resetetting");
  //   }
  // }

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
    fill(0, 80);
    rect(0, 0, width, height);

    if (alarmaDeNegro - millis() < 0) {
      println("<<< termina tiempo en negro sin buscar");
      PikamaClient.ResetBGSubtraction();
      EstadoABuscando();
    }
  }

  if (estado == ESTADO_BUSCANDO) {
    noStroke();
    fill(0, 50);
    rect(0, 0, width, height);

    int p = PikamaClient.ProximityToLines(linea, factorSonidoCercano, factorSonidoLejano);

    if (p == 2) {
      println("=== objeto intersecta la linea");      
      EstadoAArbol();
      playSonidoCerca();
    }
    else if (p == 1) {
      println("=== objeto se acerca a linea");
      playSonidoMedio();
    }
    
    // cuando no detecta personas cercanas a la linea
    // toca el sonido lejos cada 
    if (p==0 && millis()-soundTimer > soundTimeout) {
      playSonidoLejos();
      soundTimer=millis();
    }

    if (DEBUG) {
      linea.dibuja();
    }
  }

  if (estado == ESTADO_ARBOL) {
    linea.dibuja();
    pushMatrix();
    trees.draw();
    popMatrix();
    if (alarmaDeArbol - millis() < 0) {
      println("<<< termina tiempo para mostrar arbol");
      EstadoALinea();
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

  if (this.show_help) {
    fill (150);
    text("H : Show/hide this help\n\nT : Threshold \nN : Mirror vertical \nM : Mirror horizontal \nP : Limit Max area \nO : Limit Min area \nK : Change view \nR : Reset reference \nD : Show/hide debug (blobs, lines) \nC : (re)Connect with pikama server \n1 : EstadoALinea \n2 : Nueva linea fija \n3 : nueva linea fija en mouse \n4 : nueva linea lejos de blobs \n9 : mutar \n0 : EstadoANegro\nJ : probar sonido\nUP: rango de sonido cercano\nDOWN: rango de sonido lejano", 30, 30);
  }

  if (DEBUG) {
    pushMatrix();
    fill(200,200,200,50);
    rect(0,0, map(factorSonidoCercano,1,20,0,width), 3 );
    rect(0,4, map(factorSonidoLejano,1,4,0,width), 3 );
    // textSize(6);
    // fill(0);
    // text(factorSonidoCercano, 0,6);
    // text(factorSonidoLejano, 0,12);
    popMatrix();
  }
}


void EstadoABuscando() {
  estado = ESTADO_BUSCANDO;
  println ("ESTADO BUSCANDO");
  PikamaClient.ResetBGSubtraction();
}

void EstadoANegro() {
  estado = ESTADO_NEGRO;
  println("ESTADO NEGRO");
  alarmaDeNegro = millis() + MAX_TIEMPONEGRO;
  // resetBGTimer = int(frameRate*1.5);
  // println(millis() + " : ask to reset");
}
void EstadoALinea() {
  animar_linea=true;
  alarmaDeLinea = millis() + MAX_TIEMPOLINEA;
  recargaLinea();
  estado = ESTADO_LINEA;
  println("ESTADO LINEA");
}
void EstadoAArbol() {
  estado = ESTADO_ARBOL;
  alarmaDeArbol = millis() + MAX_TIEMPOARBOL;
  trees = new Trees(linea, 5, 10);
  println("ESTADO ARBOL");
}

void recargaLinea() {
  if (PikamaClient.lastCrossedBlob != null && random(1)>0.6) 
    linea.nuevaLineaEncierrona(PikamaClient.lastCrossedBlob);
  else
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
    PikamaClient.CommandServer("view");
  }
  else if (keyCode=='H') {
    show_help = !show_help;
  }
  else if (keyCode=='J') {
    playSonidoMedio();
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

  else if (keyCode==UP) {
    factorSonidoCercano += 1;
  }
  else if (keyCode==DOWN) {
    factorSonidoLejano += 0.1;
  }

  if (factorSonidoCercano>20) factorSonidoCercano=1;
  if (factorSonidoLejano>4) factorSonidoLejano=1;
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
