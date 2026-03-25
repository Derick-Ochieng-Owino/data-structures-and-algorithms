#include <stdio.h>
#include <stdlib.h>
using namespace std;

struct Node{
    int data;
    struct Node *next;
};

struct Node *front = NULL;
struct Node *rear = NULL;

void dequeue();
void enqueue(int value);

int main(){
    enqueue(10);
    enqueue(20);
    enqueue(30);
    dequeue();
}

void enqueue(int value){
    struct Node *ptr = malloc(sizeof(struct Node));
    ptr -> data = value;
    ptr -> next = NULL;

    if (front == NULL && rear == NULL){
        front = ptr;
        rear = ptr;
    }else{
        rear -> next = ptr;
        rear = ptr;
    }
}

void dequeue(){
    if(front == NULL && rear == NULL){
        printf("Empty queue");
    }else if(front == rear){
        struct Node *temp = front;
        front = NULL;
        rear = NULL;
        free(temp);
    }else{
        struct Node *temp = front;
        front = front -> next;
        free(temp);
    }
}