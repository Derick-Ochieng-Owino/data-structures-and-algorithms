#include <stdlib.h>
#include <iostream>

using namespace std;

struct Stack {
    int data;
    struct Stack *link;
};

struct Stack *top = NULL;

void push(int value);
void pop();
void display();

int main(){
    push(30);
    push(45);

    display();

    cout << "Popping...\n";
    pop();

    display();

    return 0;
}

void push(int value){
    struct Stack *ptr = (struct Stack*) malloc(sizeof(struct Stack));

    cout << "Creating new node with value: " << value << endl;
    //cout << "Input the number you want to add to the stack: ";

    ptr->data = value;
    ptr->link = NULL;

    if(top == NULL){
        cout << "Stack was empty. New node is now top.\n";
        top = ptr;
    } else {
        cout << "Linking new node to previous top.\n";
        ptr->link = top;
        top = ptr;
    }

    cout << "Push complete. Top is now: " << top->data << "\n\n";
}

void pop(){
    if (top == NULL){
        cout << "Stack is Empty. Cannot pop.\n";
    } else {
        struct Stack *temp = top;
        cout << "Removing node with value: " << temp->data << endl;

        top = top->link;   // FIX: move top down
        free(temp);

        if(top != NULL)
            cout << "New top is: " << top->data << "\n\n";
        else
            cout << "Stack is now empty.\n\n";
    }
}

void display(){
    struct Stack *temp = top;

    cout << "Current Stack: ";
    if(temp == NULL){
        cout << "Empty\n\n";
        return;
    }

    while(temp != NULL){
        cout << temp->data << " -> ";
        temp = temp->link;
    }
    cout << "NULL\n\n";
}