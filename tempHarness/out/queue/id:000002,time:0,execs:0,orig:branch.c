int foo(int a) {
    a = 6;
    if(a > 5){
        return a;         // live
    } else {
        int y = 42;       // dead
    }
    return 0;
}