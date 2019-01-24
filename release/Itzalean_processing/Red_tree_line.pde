/* OpenProcessing Tweak of *@*http://www.openprocessing.org/sketch/144159*@* */
/* !do not delete the line above, required for linking your tweak if you upload again */
class Pathfinder {
  PVector lastLocation;
  PVector location;
  PVector velocity;
  PVector direction;
  float diameter;
  boolean isFinished;
  int jumps_left = 0;
  
  Pathfinder(int x, int y, int len) {
    this.jumps_left = len;
    location = new PVector(x, y); // modificar a puntos guardados
    lastLocation = new PVector(location.x, location.y);
    velocity = new PVector(   random(5,8)*(random(1)>0.5?-1:1),
                              random(5,8)*(random(1)>0.5?-1:1) ); //velocidad //<>//
    diameter = random(2, 3); //gordura stroke
    isFinished = false;
  }

  Pathfinder(Pathfinder parent) {
    location = parent.location.get();
    lastLocation = parent.lastLocation.get();
    velocity = parent.velocity.get();
    isFinished = parent.isFinished;
  }

  void update() {
    if (isFinished) return;
    if (this.jumps_left<=0) isFinished = true;

    this.jumps_left --;
    this.lastLocation.set(location.x, location.y);

    PVector bump = new PVector(random(-1, 1), random(-1, 1));
    velocity.normalize();
    bump.mult(0.75); //- recto + doblado
    velocity.mult(1.5); //lejos
    velocity.add(bump);
    velocity.mult(random(10, 20)); 
    location.add(velocity);

    this.diameter = max(0,min(this.jumps_left,2));
    stroke(47+20, 250, 200+20,240);
    strokeWeight(this.diameter);
    line(this.lastLocation.x, this.lastLocation.y, this.location.x, this.location.y);
  }
}

class Tree {
  Pathfinder[] paths;
  int num;
  boolean isFinished = false;

  Tree (Linea l, int len) {
    int s = int(random(0, l.max_segmentos));
    int x = int(l.puntos[s].x);
    int y = int(l.puntos[s].y);
    this.start(x, y, len);
    // println(x+" "+y);
  }

  void draw() {
    for (int i = 0; i < this.paths.length; i++) {
      this.paths[i].update();
      this.isFinished = this.paths[i].isFinished;
    }
  }

  void start(int x, int y, int len) {
    this.num = 2;
    this.paths = new Pathfinder[this.num];
    for(int i = 0; i < this.num; i++) this.paths[i] = new Pathfinder(x,y, len);

    this.paths[0] = new Pathfinder(x,y, len);
  }
}


class Trees {
  Tree[] trees;
  boolean enable = false;
  
  Trees(){
    this.trees = new Tree[1];
    this.trees[0] = new Tree(new Linea(1), 5);
    this.enable = false;
  }

  Trees(Linea l, int quantity, int len){
    this.trees = new Tree[quantity];
    for (int i=0; i<this.trees.length; i++) {
      this.trees[i] = new Tree(l, len);
    }
    this.enable = true;
  }

  void draw(){
    // if (! this.enable) return;
    for (int i=0; i<trees.length; i++) {
      trees[i].draw();
    }
    this.enable = trees[0].paths[0].isFinished;
  }
}
