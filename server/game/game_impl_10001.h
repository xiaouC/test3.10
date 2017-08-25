#pragma once
#include "game_impl_base.h"

class game_impl_base {
public:
    void display();
    void display(int a);

protected:
};

void TestLib::display() {
    cout<<"First display"<<endl;
}

extern "C" {
    TestLib obj;
    void display() {
        obj.display();
    }
    void display_int() {
        obj.display(2);
    }
}
