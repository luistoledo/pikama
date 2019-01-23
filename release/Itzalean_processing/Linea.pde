class Linea { //<>//
  public int max_segmentos;
  public PVector[] puntos;

  public float minX, minY, maxX, maxY, boundW, boundH;






  // almacena el máximo de segmentos y crea el array de puntos
  Linea(int _segmentos) {
    max_segmentos = _segmentos;
    puntos = new PVector[max_segmentos];
    for (int i=0; i<max_segmentos; i++) { 
      puntos[i] =  new PVector();
    }
  }


  private void ResetMaxMins() {
    minX = width;
    maxX = 0;
    minY = height;
    maxY = 0;
    for (int i=0; i<max_segmentos; i++) {
      minX = min(puntos[i].x, minX);
      maxX = max(puntos[i].x, maxX);
      minY = min(puntos[i].y, minY);
      maxY = max(puntos[i].y, maxY);
    }
    //println("nueva linea entre: "+(int)minX+","+(int)maxX+"  "+(int)minY+","+(int)maxY);
    //rect(boundX,boundY,boundW,boundH);
    boundW = maxX - minX;
    boundH = maxY - minY;
  }




  // rellena los puntos con aleatórios de arriba a abajo
  public void nuevaAleatoriaVertical(float rnd) {
    float rangoY = width * 2.5 / max_segmentos;
    puntos[0] = new PVector(random(0, width), 0);
    for (int i=1; i<max_segmentos; i++) {
      float nextx = puntos[i-1].x + (int)random(-60, 60)*rnd;
      float nexty = puntos[i-1].y + (int)random(0, rangoY)*rnd;

      puntos[i] = new PVector(nextx, nexty);
    }
    // toma el último punto y mueve su Y al fondo de la ventana
    puntos[max_segmentos-1].y = height;
    ResetMaxMins();
    println("nueva linea entre: "+(int)minX+","+(int)maxX+"  "+(int)minY+","+(int)maxY);
  }






  // traza una linea entre dos puntos
  public void nuevaFija(float x1, float y1, float x2, float y2, float rnd) {
    puntos[0] = new PVector(x1, y1); // punto de inicio
    puntos[max_segmentos-1] = new PVector(x2, y2); // punto final

    // luego subdivide en partes iguales con la función lerp
    // y luego suma un random para que varíe un poco
    for (int i=1; i<max_segmentos-1; i++) {
      puntos[i] = PVector.lerp( puntos[0], 
        puntos[max_segmentos-1], 
        (float)i/(max_segmentos-1) );
      puntos[i].x += rnd*random(-60, 60);
      puntos[i].y += rnd*random(-20, 20);
    }
    ResetMaxMins();
    println("nueva linea entre: "+(int)minX+","+(int)maxX+"  "+(int)minY+","+(int)maxY);
  }





  // genera una linea perpendicular entre el mouse y el centro del a ventana
  public void nuevaLineaEncierrona() {
    // determina las zonas a separar
    PVector zonaA = new PVector(mouseX, mouseY);
    PVector zonaB = new PVector(width/2, height/2);

    // encuentra un punto a la mitad de esas dos zonas
    PVector mitad = PVector.lerp(zonaA, zonaB, 0.6);

    // determina un punto de tangente: invirtiendo los ejes y usando con la diferencia entre ellos (because math)
    PVector tangent = new PVector(zonaB.y - mitad.y, mitad.x - zonaB.x);
    tangent.normalize();
    tangent.mult(height);

    // utiliza la función para generar una linea fija, pero en las coordenadas de la tangente
    nuevaFija( mitad.x - tangent.x, 
      mitad.y - tangent.y, 
      mitad.x + tangent.x, 
      mitad.y + tangent.y, 
      0.4); // esto control cuanto random sobre la linea recta

    ResetMaxMins();
    println("nueva linea entre: "+(int)minX+","+(int)maxX+"  "+(int)minY+","+(int)maxY);
  }





  public void dibuja() {
    if (DEBUG) {
      pushMatrix();
      stroke(250);
      noFill();
      // rect(linea.minX, linea.minY, linea.boundW, linea.boundH);
      popMatrix();
    }

    pushMatrix();
    stroke(47, 250, 200, 150);
    strokeWeight(1);
    if (DEBUG){stroke(147, 200, 200, 10); strokeWeight(4); }

    for (int i=1; i<max_segmentos; i++) {
      // esto es para dibujar los puntos en cada vértice, solo para las pruebas
      //strokeWeight(6);point(puntos[i-1].x,puntos[i-1].y);strokeWeight(2);

      line (puntos[i-1].x, 
        puntos[i-1].y, 
        puntos[i].x, 
        puntos[i].y);
    }
    popMatrix();
  }




  // modifica cada punto de la linea aleatoriamente
  public void muta(int amt) {
    muta(amt, amt);
  }


  public void muta(int mutacionX, int mutacionY) {
    for (int i=0; i<max_segmentos; i++) {
      puntos[i].x += random(-mutacionX, mutacionX);
      puntos[i].y += random(-mutacionY, mutacionY);
    }
    ResetMaxMins();
  }


  // para poner todos los segmentos a cero (no se usa)
  public void clean() {
    for (int i=0; i<max_segmentos; i++) {
      puntos[i] = new PVector(0,0,0);
    }
  }
}
