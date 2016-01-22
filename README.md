# Wiki Category Classifier

## Summary
I downloaded all the pages in a category, as well as pages in the first-level of subcategories. This resulted in 
___ pages, with these many in each category. 

For each page, I collected the alpha-numeric text, number of images (excluding tex images), number of tex images, 
number of links, and number of citations. 

I created a tf-idf matrix from the for modelling. I have not used the extra information on images and equations. 

## Model:
I trained a Logistic Regression classifier, which gave me an accuracy of 80%. I have not adjusted for class imbalance yet. 


## Interesting facts:

- Similar categories: I took the mean tf-idf vector in each category and calculated the cosine-similarity. 


cosine-similarity  | Category | Other Category 
:------:|:------------------:  | :------:
0.876 	|      Medical_devices | Machine_learning_algorithms  
0.836 	| Congenital_disorders | Rare_diseases  
0.646 	|               Cancer | Rare_diseases  
0.610 	|  Infectious_diseases | Rare_diseases  
0.594 	|     Organs_(anatomy) | Rare_diseases  
0.541 	|     Organs_(anatomy) | Medical_devices  
0.530 	| Congenital_disorders | Infectious_diseases  
0.526 	| Congenital_disorders | Organs_(anatomy)  
0.499 	|        Rare_diseases | Medical_devices  
0.481 	|  Infectious_diseases | Medical_devices  
0.470 	|  Infectious_diseases | Organs_(anatomy)  
0.469 	|     Organs_(anatomy) | Machine_learning_algorithms  
0.460 	| Congenital_disorders | Medical_devices  
0.450 	|  Infectious_diseases | Machine_learning_algorithms  
0.448 	|               Cancer | Infectious_diseases  
0.437 	|        Rare_diseases | Machine_learning_algorithms  
0.408 	|               Cancer | Machine_learning_algorithms  
0.403 	|               Cancer | Organs_(anatomy)  
0.402 	|               Cancer | Medical_devices  
0.384 	| Congenital_disorders | Cancer  
0.383 	| Congenital_disorders | Machine_learning_algorithms  



- Here's a table that list the mean number of images, citations etc: 

images |math-equations  | links | citations | category
:---:|:-----:|:-------:|:-------:|:-------
5.85 |  0.00 |  244.21 |  14.45  | Congenital_disorders  
6.26 |  0.01 |  200.79 |  17.77  | Cancer  
6.83 |  0.00 |  298.54 |  28.22  | Infectious_diseases  
8.04 |  0.13 |  253.56 |  17.13  | Organs_(anatomy)  
5.62 |  0.01 |  280.42 |  21.79  | Rare_diseases  
5.42 |  0.42 |  179.12 |  22.72  | Medical_devices  
5.87 |  1.60 |  187.19 |  22.67  | Machine_learning_algorithms  
