import processing.sound.*;

ArrayList<SoundFile> sonidosCerca = new ArrayList<SoundFile>();
ArrayList<SoundFile> sonidosMedio = new ArrayList<SoundFile>();
ArrayList<SoundFile> sonidosLejos = new ArrayList<SoundFile>();
SoundFile currentSound;

void loadSounds() {
  for (int i=1; i<=16; i++) {
    sonidosCerca.add( new SoundFile(this, "Sonidos/Cerca/cerca_"+i+".wav") );
  }
  for (int i=1; i<=17; i++) {
    sonidosMedio.add( new SoundFile(this, "Sonidos/Medio/medio_"+i+".wav") );
  }
  for (int i=1; i<=8; i++) {
    sonidosLejos.add( new SoundFile(this, "Sonidos/Lejos/lejos_"+i+".wav") );
  }
  
  currentSound = sonidosCerca.get(0);
}

void playSonidoCerca() {
  int id = (int) random(1,sonidosCerca.size());
  playSonidoCerca(id);
}
void playSonidoCerca(int id) {
  if (! currentSound.isPlaying()) {
    currentSound = sonidosCerca.get(id);
    currentSound.play();
  }
}

void playSonidoMedio() {
  int id = (int) random(1,sonidosMedio.size());
  playSonidoMedio(id);
}
void playSonidoMedio(int id) {
  if (! currentSound.isPlaying()) {
    currentSound = sonidosMedio.get(id);
    currentSound.play();
  }
}


void playSonidoLejos() {
  int id = (int) random(1,sonidosLejos.size());
  playSonidoLejos(id);
}
void playSonidoLejos(int id) {
  if (! currentSound.isPlaying()) {
    currentSound = sonidosLejos.get(id);
    currentSound.play();
  }
}
