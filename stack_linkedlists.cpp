#include <stdio.h>
#include <stdlib.h>

struct Stack {
    int data;
    struct Stack *link;
};

struct Stack *top = NULL;

void push(int value);
void pop();
void display();
void peek();
void reverse();

int main() {
    int choice, value;

    while (true) {
        printf("\n--- STACK OPERATIONS ---\n");
        printf("1. Push\n");
        printf("2. Pop\n");
        printf("3. Display\n");
        printf("4. Peek\n");
        printf("5. Reverse\n");
        printf("6. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                printf("Enter value to push: ");
                scanf("%d", &value);
                push(value);
                break;
            case 2:
                pop();
                break;
            case 3:
                display();
                break;
            case 4:
                peek();
                break;
            case 5:
                reverse();
                break;
            case 6:
                printf("Exiting program...\n");
                return 0;
            default:
                printf("Invalid choice. Try again.\n");
        }
    }

    return 0;
}

void push(int value) {
    struct Stack *ptr = (struct Stack*) malloc(sizeof(struct Stack));

    if (ptr == NULL) {
        printf("Memory allocation failed.\n");
        return;
    }

    ptr->data = value;
    ptr->link = top;
    top = ptr;

    printf("%d pushed into stack.\n", value);
}

void pop() {
    if (top == NULL) {
        printf("Stack is empty. Nothing to pop.\n");
        return;
    }

    struct Stack *temp = top;
    int removed = temp->data;
    top = top->link;
    free(temp);

    printf("%d popped from stack.\n", removed);
}

void display() {
    if (top == NULL) {
        printf("Stack is empty.\n");
        return;
    }

    struct Stack *temp = top;
    printf("Stack elements (top to bottom): ");
    while (temp != NULL) {
        printf("%d -> ", temp->data);
        temp = temp->link;
    }
    printf("NULL\n");
}

void peek() {
    if (top == NULL) {
        printf("Stack is empty.\n");
    } else {
        printf("Top element is: %d\n", top->data);
    }
}

void reverse(){
    struct Stack *prev = NULL;
    struct Stack *current = top;
    struct Stack *next = NULL;

    while(current != NULL){
        next = current->link;     // store next
        current->link = prev;     // reverse link
        prev = current;           // move prev forward
        current = next;           // move current forward
    }

    top = prev;
    display();
}