#include <stdio.h>

int main(){
    int numbers[10] = {23,45,76,23,56,67,89,12,15,17};
    int i, j, temp;

    for(i = 1; i < 10; i++){
        for(j = 0; j < 10; j++){
            if(numbers[j] > numbers[j+1]){
                numbers[j] = numbers[j+1];
                numbers[j+1] = numbers[j];
            }
        }
    }
    return 0;
}