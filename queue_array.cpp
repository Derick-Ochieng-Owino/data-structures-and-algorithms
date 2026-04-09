#include <stdio.h>
#include <iostream>
#include <stdlib.h>

void enqueue(int value);
void dequeue();
int main(){

}

void enqueue(int value){
    if(rear == 4 - 1){
        printf("Queue is full!!");
    }else if(rear == -1 && front == -1){
        front = front + 1;
        rear = rear + 1;
        queue[rear] = element;
    }else{
        rear = rear + 1;
        queue[rear] = element;
    }
}

void dequeue(){
    if(rear == -1 && front == -1){
        printf("Queue is empty!!");
    }else if(rear == front){
        rear = front = -1;
    }else{
        front = (front + 1) % size;
    }
}